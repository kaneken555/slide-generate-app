# ai_service/capabilities/capability_base.py
#
# Base class for Capability layer.
# Each Capability provides specific business functionality (outline generation, slide generation, etc.)
# and uses Providers to implement high-level abstractions.

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional
from dataclasses import dataclass

from provider.types import Provider, ExecCtx
from provider.core.trace.tracer import span
from provider.core.metrics.recorder import record
from provider.core.utils.logger import log


@dataclass
class CapabilityConfig:
    """Capability-specific configuration"""
    pass


class CapabilityBase(ABC):
    """
    Base class for Capability layer

    Capabilities execute high-level business logic (outline generation, slide generation, etc.)
    using one or more Providers, handling request transformation, execution, and response normalization.
    """

    def __init__(self, config: Optional[CapabilityConfig] = None):
        """
        Args:
            config: Capability-specific configuration
        """
        self.config = config or CapabilityConfig()

    @abstractmethod
    def id(self) -> str:
        """Capability ID (e.g., "refine", "slidegen")"""
        raise NotImplementedError

    @abstractmethod
    def name(self) -> str:
        """Capability name (e.g., "Refine Service", "Slide Generation Service")"""
        raise NotImplementedError

    def description(self) -> str:
        """Capability description (optional)"""
        return ""

    @abstractmethod
    async def execute(self, req: Mapping[str, Any], ctx: ExecCtx) -> Mapping[str, Any]:
        """
        Main capability processing

        Args:
            req: Request parameters (defined by child class)
            ctx: Execution context

        Returns:
            Result (defined by child class)

        Raises:
            Various errors (propagated from Provider layer)
        """
        raise NotImplementedError

    async def _execute_with_observability(
        self,
        req: Mapping[str, Any],
        ctx: ExecCtx,
        operation: str
    ) -> Mapping[str, Any]:
        """
        Execution helper with observability (trace/metrics/log)

        Can be used within child class execute() methods.

        Args:
            req: Request
            ctx: Context
            operation: Operation name (used for span name)

        Returns:
            Execution result
        """
        async with span(f"{self.id()}.{operation}", {"request_id": ctx.request_id}):
            try:
                result = await self._do_execute(req, ctx)
                record(self.id(), "success", 1, {"op": operation})
                log(self.id(), "ok", request_id=ctx.request_id, operation=operation)
                return result
            except Exception as e:
                record(self.id(), "error", 1, {"op": operation, "error": type(e).__name__})
                log(self.id(), "error", request_id=ctx.request_id, operation=operation, error=str(e))
                raise

    @abstractmethod
    async def _do_execute(self, req: Mapping[str, Any], ctx: ExecCtx) -> Mapping[str, Any]:
        """
        Actual execution logic (implemented by child class)

        Called from _execute_with_observability().
        """
        raise NotImplementedError
