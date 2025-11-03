# orchestrator/api/controller.py
#
# API Controller
#
# REST API endpoints for orchestrator layer
# This is a framework-agnostic controller that can be wrapped with FastAPI, Flask, etc.

from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, Field
import uuid
import asyncio

from provider.types import ExecCtx
from provider.openai import OpenAIProvider
from provider.presenton import PresentonProvider
from ai_service.capabilities.refine_service import RefineService
from ai_service.capabilities.slidegen_service import SlideGenService
from orchestrator.runtime.refine_to_slide_workflow import RefineToSlideWorkflow
from orchestrator.state.job_registry import get_job_registry, JobStatus


# Request/Response Models

class CreateSlideRequest(BaseModel):
    """Request to create slides"""
    topic: str = Field(..., description="Slide topic", min_length=1, max_length=500)
    n_slides: int = Field(..., ge=1, le=50, description="Number of slides (1-50)")
    language: str = Field(default="Japanese", description="Output language")
    template: str = Field(default="general", description="Template name")
    export_as: str = Field(default="pptx", description="Export format (pptx, pdf, etc.)")
    refine_temperature: float = Field(default=0.3, ge=0.0, le=2.0, description="Refine temperature")
    custom_instructions: Optional[str] = Field(default=None, description="Custom instructions")


class CreateSlideResponse(BaseModel):
    """Response for create slides"""
    job_id: str = Field(..., description="Job ID")
    status: str = Field(..., description="Job status")
    status_url: str = Field(..., description="URL to check job status")


class JobStatusResponse(BaseModel):
    """Response for job status"""
    job_id: str
    workflow_id: str
    status: str
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    result: Optional[dict]
    error: Optional[str]


class SlideAPIController:
    """
    Slide API Controller

    Framework-agnostic controller for slide generation API.
    Can be wrapped with FastAPI, Flask, etc.
    """

    def __init__(self):
        """Initialize controller"""
        self.job_registry = get_job_registry()

        # Initialize providers and services
        # In production, use dependency injection
        self.openai_provider = OpenAIProvider()
        self.presenton_provider = PresentonProvider()

        self.refine_service = RefineService(self.openai_provider)
        self.slidegen_service = SlideGenService(self.presenton_provider)

    async def create_slides(self, request: CreateSlideRequest) -> CreateSlideResponse:
        """
        Create slides asynchronously

        Args:
            request: Slide creation request

        Returns:
            Response with job_id and status URL
        """
        # Generate job ID
        job_id = str(uuid.uuid4())
        workflow_id = "refine_to_slide"

        # Create job in registry
        await self.job_registry.create_job(
            job_id=job_id,
            workflow_id=workflow_id,
            input_data=request.model_dump()
        )

        # Start workflow asynchronously (fire and forget)
        asyncio.create_task(
            self._execute_workflow_async(
                job_id=job_id,
                workflow_id=workflow_id,
                input_data=request.model_dump()
            )
        )

        # Return immediately
        return CreateSlideResponse(
            job_id=job_id,
            status="pending",
            status_url=f"/api/v1/slides/{job_id}"
        )

    async def get_job_status(self, job_id: str) -> JobStatusResponse:
        """
        Get job status

        Args:
            job_id: Job ID

        Returns:
            Job status response

        Raises:
            ValueError: If job not found
        """
        job = await self.job_registry.get_job(job_id)

        if not job:
            raise ValueError(f"Job {job_id} not found")

        return JobStatusResponse(
            job_id=job.job_id,
            workflow_id=job.workflow_id,
            status=job.status.value,
            created_at=job.created_at.isoformat(),
            started_at=job.started_at.isoformat() if job.started_at else None,
            completed_at=job.completed_at.isoformat() if job.completed_at else None,
            result=job.result,
            error=job.error
        )

    async def _execute_workflow_async(
        self,
        job_id: str,
        workflow_id: str,
        input_data: dict
    ):
        """
        Execute workflow asynchronously

        Args:
            job_id: Job ID
            workflow_id: Workflow ID
            input_data: Input data
        """
        try:
            # Update status to running
            await self.job_registry.update_status(job_id, JobStatus.RUNNING)

            # Create execution context
            ctx = ExecCtx(
                request_id=job_id,
                trace_id=job_id,
                timeout_ms=180000  # 3 minutes
            )

            # Create and execute workflow
            workflow = RefineToSlideWorkflow(
                refine_service=self.refine_service,
                slidegen_service=self.slidegen_service
            )

            result = await workflow.execute(input_data, ctx)

            # Update status to completed
            await self.job_registry.update_status(
                job_id=job_id,
                status=JobStatus.COMPLETED,
                result=result
            )

        except Exception as e:
            # Update status to failed
            await self.job_registry.update_status(
                job_id=job_id,
                status=JobStatus.FAILED,
                error=str(e)
            )


# Global controller instance
_global_controller: Optional[SlideAPIController] = None


def get_controller() -> SlideAPIController:
    """Get global controller instance"""
    global _global_controller
    if _global_controller is None:
        _global_controller = SlideAPIController()
    return _global_controller
