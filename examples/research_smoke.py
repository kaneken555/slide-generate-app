# examples/research_smoke.py
#
# ResearchService smoke test
#
# Tests the ResearchService with different depth levels

import os
import anyio
from provider.types import ExecCtx
from provider.openai import OpenAIProvider
from ai_service.capabilities.research_service import ResearchService


async def test_basic_research():
    """Basic research test"""
    print("\n" + "=" * 60)
    print("ResearchService Test: Basic Depth")
    print("=" * 60)

    assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY is required"

    provider = OpenAIProvider()
    service = ResearchService(provider)
    ctx = ExecCtx(request_id="req-research-basic", trace_id="trace-research-1", timeout_ms=60000)

    result = await service.execute({
        "topic": "Quantum Computing",
        "language": "Japanese",
        "depth": "basic",
        "temperature": 0.3
    }, ctx)

    print(f"\nService: {service.name()} ({service.id()})")
    print(f"Topic: {result['topic']}")
    print(f"\n--- Summary ---")
    print(result['summary'])
    print(f"\n--- Key Points ({len(result['key_points'])} points) ---")
    for i, point in enumerate(result['key_points'], 1):
        print(f"{i}. {point}")
    print(f"\n--- Token Usage ---")
    print(f"Tokens: {result['meta']}")


async def test_medium_research():
    """Medium depth research test"""
    print("\n" + "=" * 60)
    print("ResearchService Test: Medium Depth")
    print("=" * 60)

    assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY is required"

    provider = OpenAIProvider()
    service = ResearchService(provider)
    ctx = ExecCtx(request_id="req-research-medium", trace_id="trace-research-2", timeout_ms=60000)

    result = await service.execute({
        "topic": "Sustainable Energy Technologies",
        "language": "Japanese",
        "depth": "medium",
        "focus_areas": ["Solar Power", "Wind Energy", "Battery Storage"],
        "temperature": 0.3,
        "max_tokens": 1200
    }, ctx)

    print(f"\nService: {service.name()} ({service.id()})")
    print(f"Topic: {result['topic']}")
    print(f"\n--- Summary ---")
    print(result['summary'])
    print(f"\n--- Key Points ({len(result['key_points'])} points) ---")
    for i, point in enumerate(result['key_points'], 1):
        print(f"{i}. {point}")
    print(f"\n--- Detailed Information (first 500 chars) ---")
    print(result['details'][:500] + "...")
    print(f"\n--- Token Usage ---")
    print(f"Tokens: {result['meta']}")


async def main():
    """Run all research tests"""
    try:
        # Basic research test
        await test_basic_research()

        # Medium research test
        await test_medium_research()

        print("\n" + "=" * 60)
        print("All ResearchService tests completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    anyio.run(main)
