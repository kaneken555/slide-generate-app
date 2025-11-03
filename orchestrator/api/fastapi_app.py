# orchestrator/api/fastapi_app.py
#
# FastAPI Application
#
# REST API server for slide generation

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .controller import (
    get_controller,
    CreateSlideRequest,
    CreateSlideResponse,
    JobStatusResponse
)


# Create FastAPI app
app = FastAPI(
    title="Slide Generation API",
    description="AI-powered slide generation API with async workflow orchestration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "slide-generation-api",
        "version": "1.0.0"
    }


# Create slides endpoint
@app.post(
    "/api/v1/slides",
    response_model=CreateSlideResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Slides"]
)
async def create_slides(request: CreateSlideRequest):
    """
    Create slides from topic (async)

    Creates an async job to generate slides and returns immediately with job_id.
    Use GET /api/v1/slides/{job_id} to check status.

    - **topic**: The topic for slides (e.g., "Machine Learning Basics")
    - **n_slides**: Number of slides to generate (1-50)
    - **language**: Output language (default: Japanese)
    - **template**: Template name (default: general)
    - **export_as**: Export format (default: pptx)
    """
    try:
        controller = get_controller()
        response = await controller.create_slides(request)
        return response
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create slide job: {str(e)}"
        )


# Get job status endpoint
@app.get(
    "/api/v1/slides/{job_id}",
    response_model=JobStatusResponse,
    tags=["Slides"]
)
async def get_job_status(job_id: str):
    """
    Get job status

    Check the status of a slide generation job.

    Status values:
    - **pending**: Job is queued but not started
    - **running**: Job is currently executing
    - **completed**: Job finished successfully (result available)
    - **failed**: Job failed (error message available)
    """
    try:
        controller = get_controller()
        response = await controller.get_job_status(job_id)
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job status: {str(e)}"
        )


# Job registry stats endpoint (for monitoring)
@app.get("/api/v1/stats", tags=["Monitoring"])
async def get_stats():
    """
    Get job registry statistics

    Returns statistics about job execution for monitoring purposes.
    """
    from orchestrator.state.job_registry import get_job_registry

    try:
        registry = get_job_registry()
        stats = registry.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


# Exception handlers
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    """Handle Pydantic validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected errors"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error": str(exc)
        }
    )
