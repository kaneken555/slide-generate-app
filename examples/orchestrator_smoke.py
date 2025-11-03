# examples/orchestrator_smoke.py
#
# Orchestrator layer smoke test
#
# Tests the SlideGenerationWorkflow orchestrator

import os
import anyio
from provider.types import ExecCtx
from provider.openai import OpenAIProvider
from provider.presenton import PresentonProvider
from ai_service.capabilities.research_service import ResearchService
from ai_service.capabilities.refine_service import RefineService
from ai_service.capabilities.slidegen_service import SlideGenService
from orchestrator.runtime.slide_generation_workflow import SlideGenerationWorkflow


async def test_slide_generation_workflow():
    """Test SlideGenerationWorkflow orchestrator"""
    print("\n" + "=" * 70)
    print("ORCHESTRATOR TEST: SlideGenerationWorkflow")
    print("=" * 70)

    # Prerequisites
    assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY is required"

    # Setup providers
    openai_provider = OpenAIProvider()
    presenton_provider = PresentonProvider()

    # Setup capability services
    research_service = ResearchService(openai_provider)
    refine_service = RefineService(openai_provider)
    slidegen_service = SlideGenService(presenton_provider)

    # Create workflow
    workflow = SlideGenerationWorkflow(
        research_service=research_service,
        refine_service=refine_service,
        slidegen_service=slidegen_service
    )

    print(f"Workflow: {workflow.name()} (ID: {workflow.id()})")
    print(f"Description: {workflow.description()}")
    print(f"Steps: {len(workflow.get_steps())}")
    for i, step in enumerate(workflow.get_steps(), 1):
        print(f"  {i}. {step.name}")

    # Execute workflow
    print("\n" + "-" * 70)
    print("Executing workflow...")
    print("-" * 70)

    ctx = ExecCtx(
        request_id="req-workflow-test",
        trace_id="trace-workflow-1",
        timeout_ms=180000
    )

    workflow_input = {
        "topic": "Blockchain Technology and Cryptocurrencies",
        "n_slides": 6,
        "language": "Japanese",
        "research_depth": "medium",
        "focus_areas": ["Bitcoin", "Smart Contracts", "Security"],
        "template": "general",
        "export_as": "pptx"
    }

    print(f"\nInput:")
    print(f"  Topic: {workflow_input['topic']}")
    print(f"  Slides: {workflow_input['n_slides']}")
    print(f"  Language: {workflow_input['language']}")
    print(f"  Focus Areas: {workflow_input['focus_areas']}")

    try:
        result = await workflow.execute(workflow_input, ctx)

        print("\n" + "=" * 70)
        print("WORKFLOW RESULT")
        print("=" * 70)
        print(f"Success: {result['success']}")

        print(f"\nSteps Executed:")
        for step_info in result['steps']:
            status_icon = "✓" if step_info['status'] == 'completed' else "✗"
            print(f"  {status_icon} {step_info['name']}: {step_info['status']} ({step_info['duration_ms']}ms)")

        if result['success']:
            print(f"\nResult:")
            res = result['result']
            print(f"  Topic: {res['topic']}")
            print(f"  Research Summary: {res['research_summary'][:100]}...")
            print(f"  Key Points: {len(res['key_points'])} points")
            print(f"  Outline Length: {res['outline_length']} chars")
            print(f"  Presentation ID: {res.get('presentation_id')}")
            print(f"  File Path: {res.get('file_path')}")
            print(f"  Download URL: {res.get('download_url')}")

        print("\n" + "=" * 70)
        print("Orchestrator test completed successfully!")
        print("=" * 70)

    except Exception as e:
        print(f"\n✗ Workflow failed: {e}")
        raise


async def main():
    """Run orchestrator tests"""
    try:
        await test_slide_generation_workflow()
    except Exception as e:
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    anyio.run(main)
