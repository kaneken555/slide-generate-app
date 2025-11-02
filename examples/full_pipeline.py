# examples/full_pipeline.py
#
# Full pipeline integration test
#
# Tests the complete flow: Research -> Refine -> SlideGen
# This demonstrates the entire slide generation workflow

import os
import anyio
from provider.types import ExecCtx
from provider.openai import OpenAIProvider
from provider.presenton import PresentonProvider
from ai_service.capabilities.research_service import ResearchService
from ai_service.capabilities.refine_service import RefineService
from ai_service.capabilities.slidegen_service import SlideGenService


TOPIC = "Artificial Intelligence in Healthcare"
N_SLIDES = 7


async def main():
    """Execute full pipeline: Research -> Refine -> SlideGen"""

    # Prerequisites
    assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY is required"

    ctx = ExecCtx(request_id="req-full-pipeline", trace_id="trace-full-1", timeout_ms=180000)

    print("=" * 70)
    print("FULL PIPELINE TEST: Research -> Refine -> SlideGen")
    print("=" * 70)
    print(f"Topic: {TOPIC}")
    print(f"Number of slides: {N_SLIDES}")
    print("=" * 70)

    # ========================================
    # Step 1: ResearchService - Gather information
    # ========================================
    print("\n[Step 1] ResearchService: Gathering information about topic")
    print("-" * 70)

    openai_provider = OpenAIProvider()
    research_service = ResearchService(openai_provider)

    research_result = await research_service.execute({
        "topic": TOPIC,
        "language": "Japanese",
        "depth": "medium",
        "focus_areas": ["Current applications", "Benefits", "Challenges"],
        "temperature": 0.3,
        "max_tokens": 1200
    }, ctx)

    print(f"\n✓ Research completed")
    print(f"  Summary: {research_result['summary'][:100]}...")
    print(f"  Key Points: {len(research_result['key_points'])} points gathered")
    print(f"  Token usage: {research_result['meta']}")

    # ========================================
    # Step 2: RefineService - Create outline
    # ========================================
    print("\n[Step 2] RefineService: Creating slide outline from research")
    print("-" * 70)

    refine_service = RefineService(openai_provider)

    # Build enhanced instructions with research data
    research_context = f"""
Research Summary:
{research_result['summary']}

Key Points to Cover:
""" + "\n".join([f"- {point}" for point in research_result['key_points'][:5]])

    refine_result = await refine_service.execute({
        "topic": TOPIC,
        "n_slides": N_SLIDES,
        "language": "Japanese",
        "temperature": 0.3,
        "max_tokens": 1000,
        "custom_instructions": f"Use the following research as a basis:\n\n{research_context}"
    }, ctx)

    outline = refine_result["outline"]
    print(f"\n✓ Outline created")
    print(f"  Length: {len(outline)} characters")
    print(f"  Token usage: {refine_result['meta']}")
    print(f"\n--- Generated Outline (preview) ---")
    print(outline[:400] + "...\n")

    # ========================================
    # Step 3: SlideGenService - Generate slides
    # ========================================
    print("[Step 3] SlideGenService: Generating presentation from outline")
    print("-" * 70)

    try:
        presenton_provider = PresentonProvider()
        slidegen_service = SlideGenService(presenton_provider)

        slidegen_result = await slidegen_service.execute({
            "content": outline,
            "n_slides": N_SLIDES,
            "language": "Japanese",
            "template": "general",
            "export_as": "pptx"
        }, ctx)

        print(f"\n✓ Slides generated")
        print(f"  Presentation ID: {slidegen_result.get('presentation_id')}")
        print(f"  File Path: {slidegen_result.get('file_path')}")
        print(f"  Download URL: {slidegen_result.get('download_url')}")
        print(f"  Status: {slidegen_result.get('status')}")

    except Exception as e:
        print(f"\n⚠ SlideGen skipped (Presenton not running?): {e}")
        slidegen_result = None

    # ========================================
    # Summary
    # ========================================
    print("\n" + "=" * 70)
    print("PIPELINE SUMMARY")
    print("=" * 70)
    print(f"Topic: {TOPIC}")
    print(f"Slides: {N_SLIDES}")
    print(f"\n✓ Step 1: Research - {len(research_result['key_points'])} key points")
    print(f"✓ Step 2: Refine - {len(outline)} char outline")
    if slidegen_result:
        print(f"✓ Step 3: SlideGen - {slidegen_result.get('file_path', 'N/A')}")
    else:
        print(f"⚠ Step 3: SlideGen - Skipped")
    print("\n" + "=" * 70)
    print("Full pipeline test completed!")
    print("=" * 70)


if __name__ == "__main__":
    anyio.run(main)
