# ai_service/capabilities/research_service.py
#
# ResearchService: Topic research service
#
# Uses LLM providers to gather structured information about a given topic.
# This version uses the LLM's knowledge base (Pattern A: LLM-based)

from __future__ import annotations
from typing import Any, Mapping, Optional, List
from pydantic import BaseModel, Field

from provider.types import Provider, ExecCtx
from .capability_base import CapabilityBase, CapabilityConfig


class ResearchConfig(CapabilityConfig):
    """ResearchService-specific configuration"""
    default_temperature: float = 0.3
    default_max_tokens: int = 1000
    default_language: str = "Japanese"
    system_prompt: str = "You are a research assistant who gathers and organizes information about topics in a structured way."


class ResearchRequest(BaseModel):
    """Research request"""
    topic: str = Field(..., description="Research topic")
    language: str = Field(default="Japanese", description="Language for research output")
    depth: str = Field(default="medium", description="Research depth: basic, medium, detailed")
    focus_areas: Optional[List[str]] = Field(default=None, description="Specific areas to focus on")
    temperature: float = Field(default=0.3, ge=0.0, le=2.0, description="Generation temperature")
    max_tokens: int = Field(default=1000, ge=200, le=4000, description="Maximum tokens")
    model: Optional[str] = Field(default=None, description="Model name (uses provider default if omitted)")


class ResearchResponse(BaseModel):
    """Research response"""
    topic: str = Field(..., description="Research topic")
    summary: str = Field(..., description="Overall summary")
    key_points: List[str] = Field(default_factory=list, description="Key points")
    details: str = Field(..., description="Detailed research content")
    meta: dict[str, Any] = Field(default_factory=dict, description="Metadata (token counts, etc.)")


class ResearchService(CapabilityBase):
    """
    ResearchService: Topic research

    Takes a topic and uses an LLM provider to gather and organize
    structured information about it.

    This implementation uses the LLM's knowledge base directly (no web search).
    For more up-to-date information, consider implementing web search integration.

    Example:
        ```python
        from provider.openai import OpenAIProvider
        from ai_service.capabilities.research_service import ResearchService

        provider = OpenAIProvider()
        service = ResearchService(provider)
        result = await service.execute({
            "topic": "Machine Learning Fundamentals",
            "language": "Japanese",
            "depth": "medium"
        }, ctx)
        print(result["summary"])
        print(result["key_points"])
        ```
    """

    def __init__(self, provider: Provider, config: Optional[ResearchConfig] = None):
        """
        Args:
            provider: LLM provider (OpenAI, Ollama, etc.)
            config: ResearchService-specific configuration
        """
        super().__init__(config or ResearchConfig())
        self.provider = provider
        self.config: ResearchConfig  # type hint

    def id(self) -> str:
        return "research"

    def name(self) -> str:
        return "Research Service"

    def description(self) -> str:
        return "Gathers and organizes structured information about topics using LLM knowledge"

    async def execute(self, req: Mapping[str, Any], ctx: ExecCtx) -> Mapping[str, Any]:
        """Execute research"""
        return await self._execute_with_observability(req, ctx, "research")

    async def _do_execute(self, req: Mapping[str, Any], ctx: ExecCtx) -> Mapping[str, Any]:
        """Actual research logic"""
        # Validate request
        research_req = ResearchRequest(**req)

        # Build research prompt
        prompt = self._build_research_prompt(research_req)

        # Build provider request
        provider_req = {
            "system": self.config.system_prompt,
            "text": prompt,
            "temperature": research_req.temperature,
            "max_tokens": research_req.max_tokens,
        }

        # Add model if specified
        if research_req.model:
            provider_req["model"] = research_req.model

        # Research with LLM provider
        result = await self.provider.generate(provider_req, ctx)

        # Parse and normalize response
        content = result.get("content", "").strip()
        parsed = self._parse_research_content(content, research_req.topic)
        meta = result.get("meta", {})

        response = ResearchResponse(
            topic=research_req.topic,
            summary=parsed["summary"],
            key_points=parsed["key_points"],
            details=parsed["details"],
            meta=meta
        )

        return response.model_dump()

    def _build_research_prompt(self, req: ResearchRequest) -> str:
        """Build research prompt based on depth and focus areas"""

        # Determine research depth instructions
        depth_instructions = {
            "basic": "Provide a concise overview with 3-5 key points.",
            "medium": "Provide a comprehensive overview with detailed key points and examples.",
            "detailed": "Provide an in-depth analysis with detailed explanations, examples, and relevant context."
        }

        depth_instruction = depth_instructions.get(req.depth, depth_instructions["medium"])

        # Build base prompt
        prompt = f"""
Research Topic: {req.topic}

Please research this topic and provide information in {req.language}.

{depth_instruction}

Please structure your response as follows:

## Summary
[Brief overview of the topic in 2-3 sentences]

## Key Points
[List 5-7 important key points as bullet points]
- Point 1
- Point 2
- ...

## Detailed Information
[Provide detailed explanation covering:]
1. Definition and background
2. Main concepts and approaches
3. Real-world applications and examples
4. Important considerations
5. Related topics or future directions
"""

        # Add focus areas if specified
        if req.focus_areas:
            focus_list = "\n".join([f"- {area}" for area in req.focus_areas])
            prompt += f"\n\nPlease pay special attention to these areas:\n{focus_list}"

        return prompt.strip()

    def _parse_research_content(self, content: str, topic: str) -> dict[str, Any]:
        """
        Parse the research content into structured format

        This is a simple parser. For more robust parsing, consider using
        JSON mode or more sophisticated NLP techniques.
        """
        lines = content.split("\n")

        summary = ""
        key_points = []
        details_lines = []

        current_section = None

        for line in lines:
            line_stripped = line.strip()

            # Detect sections
            if "## Summary" in line or "##Summary" in line or line_stripped.lower().startswith("summary"):
                current_section = "summary"
                continue
            elif "## Key Points" in line or "##Key Points" in line or line_stripped.lower().startswith("key points"):
                current_section = "key_points"
                continue
            elif "## Detailed" in line or "##Detailed" in line or line_stripped.lower().startswith("detailed"):
                current_section = "details"
                continue

            # Parse content based on current section
            if current_section == "summary" and line_stripped:
                if not line_stripped.startswith("#"):
                    summary += line_stripped + " "
            elif current_section == "key_points" and line_stripped:
                if line_stripped.startswith("-") or line_stripped.startswith("*"):
                    key_points.append(line_stripped.lstrip("-*").strip())
            elif current_section == "details" and line_stripped:
                details_lines.append(line)

        # Fallback: if parsing failed, use the entire content
        if not summary and not key_points:
            summary = content[:200] + "..." if len(content) > 200 else content
            details = content
        else:
            details = "\n".join(details_lines).strip()

        return {
            "summary": summary.strip(),
            "key_points": key_points,
            "details": details or content
        }
