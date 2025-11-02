# ai_service/capabilities/slidegen_service.py
#
# SlideGenService: Slide generation service
#
# Uses slide generation providers (Presenton, etc.) to generate
# presentation files from outline text.

from __future__ import annotations
from typing import Any, Mapping, Optional
from pydantic import BaseModel, Field

from provider.types import Provider, ExecCtx
from .capability_base import CapabilityBase, CapabilityConfig


class SlideGenConfig(CapabilityConfig):
    """SlideGenService-specific configuration"""
    default_language: str = "Japanese"
    default_template: str = "general"
    default_export_as: str = "pptx"


class SlideGenRequest(BaseModel):
    """Slide generation request"""
    content: str = Field(..., description="Slide content (outline text)")
    n_slides: int = Field(..., ge=1, le=100, description="Number of slides (1-100)")
    language: str = Field(default="Japanese", description="Language")
    template: str = Field(default="general", description="Template name")
    export_as: str = Field(default="pptx", description="Export format (pptx, pdf, etc.)")


class SlideGenResponse(BaseModel):
    """Slide generation response"""
    presentation_id: Optional[str] = Field(default=None, description="Presentation ID")
    file_path: Optional[str] = Field(default=None, description="File path")
    download_url: Optional[str] = Field(default=None, description="Download URL")
    status: str = Field(default="success", description="Status")
    meta: dict[str, Any] = Field(default_factory=dict, description="Other metadata")


class SlideGenService(CapabilityBase):
    """
    SlideGenService: Slide generation

    Takes outline text and uses a slide generation provider to create
    presentation files (PPTX, PDF, etc.).
    """

    def __init__(self, provider: Provider, config: Optional[SlideGenConfig] = None):
        """
        Args:
            provider: Slide generation provider (Presenton, etc.)
            config: SlideGenService-specific configuration
        """
        super().__init__(config or SlideGenConfig())
        self.provider = provider
        self.config: SlideGenConfig  # type hint

        # Check that provider supports slide generation
        caps = provider.capabilities()
        if not caps.get("slideGen"):
            raise ValueError(
                f"Provider '{provider.id()}' does not support slide generation. "
                f"Capabilities: {caps}"
            )

    def id(self) -> str:
        return "slidegen"

    def name(self) -> str:
        return "Slide Generation Service"

    def description(self) -> str:
        return "Generates presentation files from outline text"

    async def execute(self, req: Mapping[str, Any], ctx: ExecCtx) -> Mapping[str, Any]:
        """Execute slide generation"""
        return await self._execute_with_observability(req, ctx, "slidegen")

    async def _do_execute(self, req: Mapping[str, Any], ctx: ExecCtx) -> Mapping[str, Any]:
        """Actual slide generation logic"""
        # Validate request
        slidegen_req = SlideGenRequest(**req)

        # Build provider request
        provider_req = {
            "content": slidegen_req.content,
            "n_slides": slidegen_req.n_slides,
            "language": slidegen_req.language,
            "template": slidegen_req.template,
            "export_as": slidegen_req.export_as,
        }

        # Generate with slide provider
        result = await self.provider.slide_gen(provider_req, ctx)

        # Normalize response
        response = SlideGenResponse(
            presentation_id=result.get("presentation_id"),
            file_path=result.get("file_path") or result.get("path"),  # Support "path" as well
            download_url=result.get("download_url") or result.get("edit_path"),  # Support "edit_path"
            status=result.get("status", "success"),
            meta={k: v for k, v in result.items() if k not in ["presentation_id", "file_path", "path", "download_url", "edit_path", "status"]}
        )

        return response.model_dump()
