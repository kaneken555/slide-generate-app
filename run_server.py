# run_server.py
#
# FastAPI Server Entry Point

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

if __name__ == "__main__":
    # Check required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY is not set in environment variables")
        print("Please create a .env file with OPENAI_API_KEY=your-key")
        exit(1)

    print("\n" + "=" * 70)
    print("Starting Slide Generation API Server")
    print("=" * 70)
    print(f"Environment:")
    print(f"  OPENAI_API_KEY: {'✓ Set' if os.getenv('OPENAI_API_KEY') else '✗ Not set'}")
    print(f"  OLLAMA_BASE: {os.getenv('OLLAMA_BASE', 'http://localhost:11434')}")
    print(f"\nAPI Documentation:")
    print(f"  Swagger UI: http://localhost:8000/docs")
    print(f"  ReDoc: http://localhost:8000/redoc")
    print(f"\nEndpoints:")
    print(f"  POST /api/v1/slides - Create slide generation job")
    print(f"  GET /api/v1/slides/{{job_id}} - Get job status")
    print(f"  GET /health - Health check")
    print(f"  GET /api/v1/stats - Job statistics")
    print("=" * 70 + "\n")

    # Run server
    uvicorn.run(
        "orchestrator.api.fastapi_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )
