# orchestrator/state/job_registry.py
#
# Job Registry
#
# Manages asynchronous job status and results

from __future__ import annotations
from typing import Any, Optional, Dict
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import asyncio


class JobStatus(Enum):
    """Job status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Job:
    """Job data"""
    job_id: str
    workflow_id: str
    status: JobStatus
    input_data: dict
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[dict] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "job_id": self.job_id,
            "workflow_id": self.workflow_id,
            "status": self.status.value,
            "input_data": self.input_data,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error
        }


class JobRegistry:
    """
    Job Registry

    In-memory job status management for async workflows.
    For production, consider using Redis or a database.
    """

    def __init__(self):
        """Initialize registry"""
        self._jobs: Dict[str, Job] = {}
        self._lock = asyncio.Lock()

    async def create_job(
        self,
        job_id: str,
        workflow_id: str,
        input_data: dict
    ) -> Job:
        """
        Create a new job

        Args:
            job_id: Unique job ID
            workflow_id: Workflow identifier
            input_data: Input data for the workflow

        Returns:
            Created job
        """
        async with self._lock:
            if job_id in self._jobs:
                raise ValueError(f"Job {job_id} already exists")

            job = Job(
                job_id=job_id,
                workflow_id=workflow_id,
                status=JobStatus.PENDING,
                input_data=input_data
            )

            self._jobs[job_id] = job
            return job

    async def get_job(self, job_id: str) -> Optional[Job]:
        """
        Get job by ID

        Args:
            job_id: Job ID

        Returns:
            Job or None if not found
        """
        async with self._lock:
            return self._jobs.get(job_id)

    async def update_status(
        self,
        job_id: str,
        status: JobStatus,
        result: Optional[dict] = None,
        error: Optional[str] = None
    ):
        """
        Update job status

        Args:
            job_id: Job ID
            status: New status
            result: Result data (for completed jobs)
            error: Error message (for failed jobs)
        """
        async with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                raise ValueError(f"Job {job_id} not found")

            job.status = status

            if status == JobStatus.RUNNING and not job.started_at:
                job.started_at = datetime.now()

            if status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                job.completed_at = datetime.now()

            if result:
                job.result = result

            if error:
                job.error = error

    async def list_jobs(
        self,
        workflow_id: Optional[str] = None,
        status: Optional[JobStatus] = None,
        limit: int = 100
    ) -> list[Job]:
        """
        List jobs with optional filters

        Args:
            workflow_id: Filter by workflow ID
            status: Filter by status
            limit: Maximum number of jobs to return

        Returns:
            List of jobs
        """
        async with self._lock:
            jobs = list(self._jobs.values())

            # Apply filters
            if workflow_id:
                jobs = [j for j in jobs if j.workflow_id == workflow_id]

            if status:
                jobs = [j for j in jobs if j.status == status]

            # Sort by created_at descending
            jobs.sort(key=lambda j: j.created_at, reverse=True)

            return jobs[:limit]

    async def delete_job(self, job_id: str):
        """
        Delete a job

        Args:
            job_id: Job ID
        """
        async with self._lock:
            if job_id in self._jobs:
                del self._jobs[job_id]

    async def cleanup_old_jobs(self, max_age_hours: int = 24):
        """
        Clean up old jobs

        Args:
            max_age_hours: Maximum age in hours
        """
        async with self._lock:
            now = datetime.now()
            to_delete = []

            for job_id, job in self._jobs.items():
                age = (now - job.created_at).total_seconds() / 3600
                if age > max_age_hours:
                    to_delete.append(job_id)

            for job_id in to_delete:
                del self._jobs[job_id]

    def get_stats(self) -> dict:
        """
        Get registry statistics

        Returns:
            Statistics dictionary
        """
        stats = {
            "total_jobs": len(self._jobs),
            "by_status": {}
        }

        for status in JobStatus:
            count = sum(1 for j in self._jobs.values() if j.status == status)
            stats["by_status"][status.value] = count

        return stats


# Global singleton instance
_global_registry: Optional[JobRegistry] = None


def get_job_registry() -> JobRegistry:
    """Get global job registry instance"""
    global _global_registry
    if _global_registry is None:
        _global_registry = JobRegistry()
    return _global_registry
