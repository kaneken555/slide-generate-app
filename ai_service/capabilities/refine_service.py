# ai_service/capabilities/refine_service.py
#
# RefineService: Slide outline generation service
#
# Uses LLM providers to generate structured slide outlines from topics.

from __future__ import annotations
from typing import Any, Mapping, Optional
from pydantic import BaseModel, Field

from provider.types import Provider, ExecCtx
from .capability_base import CapabilityBase, CapabilityConfig


class RefineConfig(CapabilityConfig):
    """RefineService-specific configuration"""
    default_temperature: float = 0.3
    default_max_tokens: int = 700
    default_language: str = "Japanese"
    system_prompt: str = "You are an editor who creates concise and structured slide outlines in Japanese."


class RefineRequest(BaseModel):
    """Outline generation request"""
    topic: str = Field(..., description="Slide topic")
    n_slides: int = Field(..., ge=1, le=50, description="Number of slides (1-50)")
    language: str = Field(default="Japanese", description="Language")
    temperature: float = Field(default=0.3, ge=0.0, le=2.0, description="Generation temperature")
    max_tokens: int = Field(default=700, ge=100, le=4000, description="Maximum tokens")
    model: Optional[str] = Field(default=None, description="Model name (uses provider default if omitted)")
    custom_instructions: Optional[str] = Field(default=None, description="Additional instructions (optional)")


class RefineResponse(BaseModel):
    """Outline generation response"""
    outline: str = Field(..., description="Generated outline")
    meta: dict[str, Any] = Field(default_factory=dict, description="Metadata (token counts, etc.)")


class RefineService(CapabilityBase):
    """
    RefineService: Slide outline generation

    Takes a topic and number of slides, uses an LLM provider to generate
    a structured slide outline.
    """

    def __init__(self, provider: Provider, config: Optional[RefineConfig] = None):
        """
        Args:
            provider: LLM provider (OpenAI, Ollama, etc.)
            config: RefineService-specific configuration
        """
        super().__init__(config or RefineConfig())
        self.provider = provider
        self.config: RefineConfig  # type hint

    def id(self) -> str:
        return "refine"

    def name(self) -> str:
        return "Refine Service"

    def description(self) -> str:
        return "Generates structured slide outlines from topics"

    async def execute(self, req: Mapping[str, Any], ctx: ExecCtx) -> Mapping[str, Any]:
        """Execute outline generation"""
        return await self._execute_with_observability(req, ctx, "refine")

    async def _do_execute(self, req: Mapping[str, Any], ctx: ExecCtx) -> Mapping[str, Any]:
        """Actual outline generation logic"""
        # Validate request
        refine_req = RefineRequest(**req)

        # Build prompt
        prompt = self._build_prompt(refine_req)

        # Build provider request
        provider_req = {
            "system": self.config.system_prompt,
            "text": prompt,
            "temperature": refine_req.temperature,
            "max_tokens": refine_req.max_tokens,
        }

        # Add model if specified
        if refine_req.model:
            provider_req["model"] = refine_req.model

        # Generate with LLM provider
        result = await self.provider.generate(provider_req, ctx)

        # Normalize response
        outline = result.get("content", "").strip()
        meta = result.get("meta", {})

        response = RefineResponse(outline=outline, meta=meta)
        return response.model_dump()

    def _build_prompt(self, req: RefineRequest) -> str:
        """Build outline generation prompt"""
        base_prompt = f"""
Please create a slide outline for the following theme in {req.language}.
- Theme: {req.topic}
- Number of slides: {req.n_slides}
- First slide should have title and key points, rest should be bullet-point focused
- Output as plain text (Markdown OK). Use numbered headings and bullets.

Example:
# Title
- Key Point A
- Key Point B
## Background
- ...
"""

        # Add custom instructions if provided
        if req.custom_instructions:
            base_prompt += f"\n\nAdditional instructions:\n{req.custom_instructions}"

        return base_prompt.strip()
