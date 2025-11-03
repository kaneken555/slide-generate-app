# orchestrator/runtime/slide_generation_workflow.py
#
# Slide Generation Workflow
#
# Orchestrates the full slide generation pipeline:
# Research -> Refine -> SlideGen

from __future__ import annotations
from typing import Any

from .workflow_base import WorkflowBase, WorkflowContext
from ai_service.capabilities.research_service import ResearchService
from ai_service.capabilities.refine_service import RefineService
from ai_service.capabilities.slidegen_service import SlideGenService


class SlideGenerationWorkflow(WorkflowBase):
    """
    Slide Generation Workflow

    Orchestrates the complete slide generation pipeline:
    1. Research: Gather information about the topic
    2. Refine: Create structured outline from research
    3. SlideGen: Generate presentation from outline

    Input:
        {
            "topic": str,
            "n_slides": int,
            "language": str = "Japanese",
            "research_depth": str = "medium",
            "focus_areas": list[str] = None,
            "template": str = "general",
            "export_as": str = "pptx"
        }

    Output:
        {
            "success": bool,
            "steps": [...],
            "output": {
                "research": {...},
                "outline": {...},
                "presentation": {...}
            }
        }
    """

    def __init__(
        self,
        research_service: ResearchService,
        refine_service: RefineService,
        slidegen_service: SlideGenService
    ):
        """
        Args:
            research_service: Research capability service
            refine_service: Refine capability service
            slidegen_service: Slide generation capability service
        """
        self.research_service = research_service
        self.refine_service = refine_service
        self.slidegen_service = slidegen_service
        super().__init__()

    def id(self) -> str:
        return "slide_generation"

    def name(self) -> str:
        return "Slide Generation Workflow"

    def description(self) -> str:
        return "Complete pipeline for generating slides from a topic: Research -> Refine -> SlideGen"

    def _build_steps(self):
        """Build workflow steps"""

        # Step 1: Research
        self.add_step(
            name="research",
            execute_fn=self._step_research,
            output_key="research",
            retry_count=1
        )

        # Step 2: Refine
        self.add_step(
            name="refine",
            execute_fn=self._step_refine,
            output_key="outline",
            retry_count=1
        )

        # Step 3: SlideGen
        self.add_step(
            name="slidegen",
            execute_fn=self._step_slidegen,
            output_key="presentation",
            skip_on_error=False,  # Fail workflow if slidegen fails
            retry_count=1
        )

    async def _step_research(self, ctx: WorkflowContext, step_input: dict) -> dict:
        """Step 1: Research - Gather information about topic"""
        input_data = ctx.initial_input

        research_req = {
            "topic": input_data["topic"],
            "language": input_data.get("language", "Japanese"),
            "depth": input_data.get("research_depth", "medium"),
            "focus_areas": input_data.get("focus_areas"),
            "temperature": 0.3,
            "max_tokens": 1200
        }

        result = await self.research_service.execute(research_req, ctx.exec_ctx)
        return result

    async def _step_refine(self, ctx: WorkflowContext, step_input: dict) -> dict:
        """Step 2: Refine - Create outline from research"""
        input_data = ctx.initial_input
        research_result = ctx.get("research")

        # Build custom instructions with research data
        research_context = self._build_research_context(research_result)

        refine_req = {
            "topic": input_data["topic"],
            "n_slides": input_data["n_slides"],
            "language": input_data.get("language", "Japanese"),
            "temperature": 0.3,
            "max_tokens": 1000,
            "custom_instructions": f"Use the following research as a basis:\n\n{research_context}"
        }

        result = await self.refine_service.execute(refine_req, ctx.exec_ctx)
        return result

    async def _step_slidegen(self, ctx: WorkflowContext, step_input: dict) -> dict:
        """Step 3: SlideGen - Generate presentation from outline"""
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

    def _build_research_context(self, research_result: dict) -> str:
        """Build research context string for refine step"""
        context = f"""
Research Summary:
{research_result['summary']}

Key Points to Cover:
"""
        for point in research_result['key_points'][:5]:
            context += f"- {point}\n"

        return context.strip()

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
            research = ctx.get("research", {})
            outline = ctx.get("outline", {})
            presentation = ctx.get("presentation", {})

            base_output["result"] = {
                "topic": ctx.initial_input.get("topic"),
                "n_slides": ctx.initial_input.get("n_slides"),
                "research_summary": research.get("summary", ""),
                "key_points": research.get("key_points", []),
                "outline_length": len(outline.get("outline", "")),
                "presentation_id": presentation.get("presentation_id"),
                "file_path": presentation.get("file_path"),
                "download_url": presentation.get("download_url")
            }

        return base_output
