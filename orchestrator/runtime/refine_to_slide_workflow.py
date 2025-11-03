# orchestrator/runtime/refine_to_slide_workflow.py
#
# Refine to Slide Workflow
#
# Simple 2-step workflow: Refine -> SlideGen
# Lighter alternative to full research pipeline

from __future__ import annotations
from typing import Any

from .workflow_base import WorkflowBase, WorkflowContext
from ai_service.capabilities.refine_service import RefineService
from ai_service.capabilities.slidegen_service import SlideGenService


class RefineToSlideWorkflow(WorkflowBase):
    """
    Refine to Slide Workflow

    Simple 2-step workflow for quick slide generation:
    1. Refine: Create structured outline from topic
    2. SlideGen: Generate presentation from outline

    Input:
        {
            "topic": str,
            "n_slides": int,
            "language": str = "Japanese",
            "template": str = "general",
            "export_as": str = "pptx",
            "refine_temperature": float = 0.3,
            "custom_instructions": str = None
        }

    Output:
        {
            "success": bool,
            "steps": [...],
            "output": {
                "outline": {...},
                "presentation": {...}
            }
        }
    """

    def __init__(
        self,
        refine_service: RefineService,
        slidegen_service: SlideGenService
    ):
        """
        Args:
            refine_service: Refine capability service
            slidegen_service: Slide generation capability service
        """
        self.refine_service = refine_service
        self.slidegen_service = slidegen_service
        super().__init__()

    def id(self) -> str:
        return "refine_to_slide"

    def name(self) -> str:
        return "Refine to Slide Workflow"

    def description(self) -> str:
        return "Quick slide generation: Refine -> SlideGen"

    def _build_steps(self):
        """Build workflow steps"""

        # Step 1: Refine
        self.add_step(
            name="refine",
            execute_fn=self._step_refine,
            output_key="outline",
            retry_count=1
        )

        # Step 2: SlideGen
        self.add_step(
            name="slidegen",
            execute_fn=self._step_slidegen,
            output_key="presentation",
            skip_on_error=False,
            retry_count=1
        )

    async def _step_refine(self, ctx: WorkflowContext, step_input: dict) -> dict:
        """Step 1: Refine - Create outline from topic"""
        input_data = ctx.initial_input

        refine_req = {
            "topic": input_data["topic"],
            "n_slides": input_data["n_slides"],
            "language": input_data.get("language", "Japanese"),
            "temperature": input_data.get("refine_temperature", 0.3),
            "max_tokens": input_data.get("refine_max_tokens", 1000),
            "custom_instructions": input_data.get("custom_instructions")
        }

        # Add model if specified
        if "refine_model" in input_data:
            refine_req["model"] = input_data["refine_model"]

        result = await self.refine_service.execute(refine_req, ctx.exec_ctx)
        return result

    async def _step_slidegen(self, ctx: WorkflowContext, step_input: dict) -> dict:
        """Step 2: SlideGen - Generate presentation from outline"""
        input_data = ctx.initial_input
        refine_result = ctx.get("outline")

        slidegen_req = {
            "content": refine_result["outline"],
            "n_slides": input_data["n_slides"],
            "language": input_data.get("language", "Japanese"),
            "template": input_data.get("template", "general"),
            "export_as": input_data.get("export_as", "pptx")
        }

        result = await self.slidegen_service.execute(slidegen_req, ctx.exec_ctx)
        return result

    def _build_output(self, ctx: WorkflowContext) -> dict:
        """Build final workflow output with detailed results"""
        base_output = super()._build_output(ctx)

        # Add workflow-specific output structure
        base_output["workflow"] = {
            "id": self.id(),
            "name": self.name()
        }

        # Add detailed step outputs
        if not ctx.has_errors():
            outline = ctx.get("outline", {})
            presentation = ctx.get("presentation", {})

            base_output["result"] = {
                "topic": ctx.initial_input.get("topic"),
                "n_slides": ctx.initial_input.get("n_slides"),
                "outline": outline.get("outline", ""),
                "outline_length": len(outline.get("outline", "")),
                "presentation_id": presentation.get("presentation_id"),
                "file_path": presentation.get("file_path"),
                "download_url": presentation.get("download_url"),
                "status": presentation.get("status", "success")
            }

        return base_output
