# examples/api_async_test.py
#
# Async API Integration Test
#
# Tests the async API flow: POST /api/v1/slides -> GET /api/v1/slides/{job_id}

import os
import anyio
import asyncio
from orchestrator.api.controller import get_controller, CreateSlideRequest


async def main():
    """Test async API flow"""

    print("\n" + "=" * 70)
    print("ASYNC API INTEGRATION TEST")
    print("=" * 70)

    # Prerequisites
    assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY is required"

    # Get controller
    controller = get_controller()

    # Step 1: Create slides (POST /api/v1/slides)
    print("\n[Step 1] POST /api/v1/slides - Create slide generation job")
    print("-" * 70)

    request = CreateSlideRequest(
        topic="Quantum Computing Basics",
        n_slides=5,
        language="Japanese",
        template="general",
        export_as="pptx",
        refine_temperature=0.3,
        custom_instructions="Focus on practical applications"
    )

    print(f"Request:")
    print(f"  Topic: {request.topic}")
    print(f"  Slides: {request.n_slides}")
    print(f"  Language: {request.language}")

    response = await controller.create_slides(request)

    print(f"\nResponse (202 Accepted):")
    print(f"  Job ID: {response.job_id}")
    print(f"  Status: {response.status}")
    print(f"  Status URL: {response.status_url}")

    job_id = response.job_id

    # Step 2: Poll for status (GET /api/v1/slides/{job_id})
    print(f"\n[Step 2] GET /api/v1/slides/{job_id} - Poll for status")
    print("-" * 70)

    max_attempts = 60  # 60 attempts x 2 seconds = 2 minutes
    attempt = 0

    while attempt < max_attempts:
        attempt += 1
        print(f"\nAttempt {attempt}: Checking job status...")

        try:
            status_response = await controller.get_job_status(job_id)

            print(f"  Status: {status_response.status}")

            if status_response.status == "completed":
                print(f"\n{'=' * 70}")
                print("JOB COMPLETED!")
                print("=" * 70)

                result = status_response.result

                print(f"\nWorkflow: {result.get('workflow', {}).get('name')}")
                print(f"\nSteps:")
                for step in result.get('steps', []):
                    status_icon = "✓" if step['status'] == 'completed' else "✗"
                    print(f"  {status_icon} {step['name']}: {step['status']} ({step['duration_ms']}ms)")

                if result.get('result'):
                    res = result['result']
                    print(f"\nResult:")
                    print(f"  Topic: {res.get('topic')}")
                    print(f"  Slides: {res.get('n_slides')}")
                    print(f"  Outline Length: {res.get('outline_length')} chars")
                    print(f"  Presentation ID: {res.get('presentation_id')}")
                    print(f"  File Path: {res.get('file_path')}")
                    print(f"  Download URL: {res.get('download_url')}")

                print(f"\n{'=' * 70}")
                print("Test completed successfully!")
                print("=" * 70)
                break

            elif status_response.status == "failed":
                print(f"\n{'=' * 70}")
                print("JOB FAILED!")
                print("=" * 70)
                print(f"Error: {status_response.error}")
                break

            elif status_response.status in ["pending", "running"]:
                print(f"  Job is {status_response.status}... waiting 2 seconds")
                await asyncio.sleep(2)

        except Exception as e:
            print(f"  Error checking status: {e}")
            break

    if attempt >= max_attempts:
        print(f"\n{'=' * 70}")
        print("TIMEOUT: Job did not complete within time limit")
        print("=" * 70)


if __name__ == "__main__":
    anyio.run(main)
