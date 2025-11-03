# orchestrator/runtime/workflow_base.py
#
# Base classes for workflow definition and execution

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional, Callable, List
from dataclasses import dataclass, field
from enum import Enum

from provider.types import ExecCtx
from provider.core.trace.tracer import span
from provider.core.metrics.recorder import record
from provider.core.utils.logger import log


class StepStatus(Enum):
    """Step execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """
    A single step in a workflow

    Each step has:
    - name: Unique identifier
    - execute_fn: Async function to execute
    - input_mapping: How to map workflow context to step input
    - output_key: Where to store step output in context
    - skip_on_error: Whether to skip this step if previous steps failed
    """
    name: str
    execute_fn: Callable
    input_mapping: Optional[Callable[[dict], dict]] = None
    output_key: str = "result"
    skip_on_error: bool = False
    retry_count: int = 0


@dataclass
class StepResult:
    """Result of a step execution"""
    step_name: str
    status: StepStatus
    output: Optional[dict] = None
    error: Optional[Exception] = None
    duration_ms: int = 0


@dataclass
class WorkflowContext:
    """
    Workflow execution context

    Stores all data that flows between steps
    """
    exec_ctx: ExecCtx
    initial_input: dict = field(default_factory=dict)
    step_outputs: dict[str, Any] = field(default_factory=dict)
    step_results: List[StepResult] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from step outputs"""
        return self.step_outputs.get(key, default)

    def set(self, key: str, value: Any):
        """Set value in step outputs"""
        self.step_outputs[key] = value

    def has_errors(self) -> bool:
        """Check if any step has failed"""
        return any(r.status == StepStatus.FAILED for r in self.step_results)


class WorkflowBase(ABC):
    """
    Base class for workflows

    A workflow is a sequence of steps that execute in order,
    with data flowing from one step to the next.
    """

    def __init__(self):
        """Initialize workflow"""
        self._steps: List[WorkflowStep] = []
        self._build_steps()

    @abstractmethod
    def id(self) -> str:
        """Workflow ID"""
        raise NotImplementedError

    @abstractmethod
    def name(self) -> str:
        """Workflow name"""
        raise NotImplementedError

    def description(self) -> str:
        """Workflow description"""
        return ""

    @abstractmethod
    def _build_steps(self):
        """
        Build workflow steps

        Child classes should call add_step() to define the workflow.
        """
        raise NotImplementedError

    def add_step(
        self,
        name: str,
        execute_fn: Callable,
        input_mapping: Optional[Callable[[dict], dict]] = None,
        output_key: str = "result",
        skip_on_error: bool = False,
        retry_count: int = 0
    ):
        """
        Add a step to the workflow

        Args:
            name: Step name
            execute_fn: Async function to execute (receives WorkflowContext)
            input_mapping: Function to map context to step input
            output_key: Key to store output in context
            skip_on_error: Skip if previous steps failed
            retry_count: Number of retries on failure
        """
        step = WorkflowStep(
            name=name,
            execute_fn=execute_fn,
            input_mapping=input_mapping,
            output_key=output_key,
            skip_on_error=skip_on_error,
            retry_count=retry_count
        )
        self._steps.append(step)

    def get_steps(self) -> List[WorkflowStep]:
        """Get all workflow steps"""
        return self._steps.copy()

    async def execute(self, input_data: dict, ctx: ExecCtx) -> dict:
        """
        Execute the workflow

        Args:
            input_data: Initial input data
            ctx: Execution context

        Returns:
            Final workflow output
        """
        workflow_ctx = WorkflowContext(
            exec_ctx=ctx,
            initial_input=input_data
        )

        async with span(f"workflow.{self.id()}", {"workflow": self.name()}):
            log(self.id(), "start", request_id=ctx.request_id, workflow=self.name())

            try:
                for step in self._steps:
                    await self._execute_step(step, workflow_ctx)

                record(self.id(), "success", 1, {"workflow": self.name()})
                log(self.id(), "complete", request_id=ctx.request_id, workflow=self.name())

                return self._build_output(workflow_ctx)

            except Exception as e:
                record(self.id(), "error", 1, {"workflow": self.name(), "error": type(e).__name__})
                log(self.id(), "error", request_id=ctx.request_id, workflow=self.name(), error=str(e))
                raise

    async def _execute_step(self, step: WorkflowStep, ctx: WorkflowContext):
        """Execute a single step"""
        import time

        # Check if we should skip this step
        if step.skip_on_error and ctx.has_errors():
            result = StepResult(
                step_name=step.name,
                status=StepStatus.SKIPPED
            )
            ctx.step_results.append(result)
            log(self.id(), "step_skipped", step=step.name)
            return

        start_ms = int(time.time() * 1000)

        async with span(f"workflow.step.{step.name}", {"step": step.name}):
            log(self.id(), "step_start", step=step.name)

            try:
                # Map input
                if step.input_mapping:
                    step_input = step.input_mapping(ctx.step_outputs)
                else:
                    step_input = ctx.step_outputs

                # Execute with retry
                output = await self._execute_with_retry(step, step_input, ctx)

                # Store output
                ctx.set(step.output_key, output)

                duration_ms = int(time.time() * 1000) - start_ms
                result = StepResult(
                    step_name=step.name,
                    status=StepStatus.COMPLETED,
                    output=output,
                    duration_ms=duration_ms
                )
                ctx.step_results.append(result)

                record(self.id(), "step_success", 1, {"step": step.name})
                log(self.id(), "step_complete", step=step.name, duration_ms=duration_ms)

            except Exception as e:
                duration_ms = int(time.time() * 1000) - start_ms
                result = StepResult(
                    step_name=step.name,
                    status=StepStatus.FAILED,
                    error=e,
                    duration_ms=duration_ms
                )
                ctx.step_results.append(result)

                record(self.id(), "step_error", 1, {"step": step.name, "error": type(e).__name__})
                log(self.id(), "step_failed", step=step.name, error=str(e))
                raise

    async def _execute_with_retry(self, step: WorkflowStep, step_input: dict, ctx: WorkflowContext) -> Any:
        """Execute step with retry logic"""
        last_error = None

        for attempt in range(step.retry_count + 1):
            try:
                if attempt > 0:
                    log(self.id(), "step_retry", step=step.name, attempt=attempt)

                return await step.execute_fn(ctx, step_input)

            except Exception as e:
                last_error = e
                if attempt >= step.retry_count:
                    break

        raise last_error

    def _build_output(self, ctx: WorkflowContext) -> dict:
        """
        Build final workflow output

        Child classes can override this to customize output format.
        """
        return {
            "success": not ctx.has_errors(),
            "steps": [
                {
                    "name": r.step_name,
                    "status": r.status.value,
                    "duration_ms": r.duration_ms
                }
                for r in ctx.step_results
            ],
            "output": ctx.step_outputs
        }
