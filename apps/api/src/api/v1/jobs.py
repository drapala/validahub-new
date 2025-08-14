from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
import uuid
from datetime import datetime

from src.schemas.validate import AsyncJobResponse
from src.schemas.errors import ProblemDetail

router = APIRouter(prefix="/api/v1", tags=["jobs"])

# Temporary in-memory storage for demo
# TODO: Replace with Redis or database
JOBS_STORE = {}


def get_correlation_id(
    x_correlation_id: Optional[str] = Header(None, alias="X-Correlation-Id")
) -> str:
    """Generate or return correlation ID for request tracking."""
    return x_correlation_id or str(uuid.uuid4())


@router.get(
    "/jobs/{job_id}",
    response_model=AsyncJobResponse,
    responses={
        404: {"model": ProblemDetail, "description": "Job not found"},
    },
    operation_id="getJob",
    summary="Get job status",
    description="Check the status of an asynchronous processing job"
)
async def get_job(
    job_id: str,
    correlation_id: str = Depends(get_correlation_id),
) -> AsyncJobResponse:
    """
    Get the current status of an asynchronous job.
    
    Jobs can be in one of these states:
    - accepted: Job has been accepted and queued
    - processing: Job is currently being processed
    - completed: Job has completed successfully
    - failed: Job has failed with an error
    
    When completed, the result field will contain the output data or file links.
    """
    
    # Check if job exists (in production, query from Redis/DB)
    if job_id not in JOBS_STORE:
        # For demo, create a fake job
        JOBS_STORE[job_id] = {
            "job_id": job_id,
            "status": "processing",
            "message": "Processing CSV file",
            "location": f"/api/v1/jobs/{job_id}",
            "progress": 45,
            "created_at": datetime.utcnow(),
        }
    
    job = JOBS_STORE[job_id]
    
    # Simulate job progression for demo
    if job["status"] == "processing" and job.get("progress", 0) >= 100:
        job["status"] = "completed"
        job["completed_at"] = datetime.utcnow()
        job["result"] = {
            "files": {
                "corrected_csv": f"https://storage.validahub.com/jobs/{job_id}/corrected.csv",
                "report_json": f"https://storage.validahub.com/jobs/{job_id}/report.json",
                "rejected_rows": f"https://storage.validahub.com/jobs/{job_id}/rejected.csv",
            },
            "summary": {
                "total_corrections": 145,
                "success_rate": 98.5,
                "total_rows": 1000,
                "corrected_rows": 145,
                "rejected_rows": 5
            }
        }
        job["message"] = "Job completed successfully"
    elif job["status"] == "processing":
        # Increment progress for demo
        job["progress"] = min(job.get("progress", 0) + 25, 100)
    
    return AsyncJobResponse(**job)


def create_job(job_type: str, metadata: dict = None) -> AsyncJobResponse:
    """
    Create a new job and add it to the store.
    Used internally by other endpoints when async processing is needed.
    """
    job_id = str(uuid.uuid4())
    job = AsyncJobResponse(
        job_id=job_id,
        status="accepted",
        message=f"{job_type} job accepted for processing",
        location=f"/api/v1/jobs/{job_id}",
        progress=0,
        created_at=datetime.utcnow()
    )
    
    JOBS_STORE[job_id] = job.model_dump()
    if metadata:
        JOBS_STORE[job_id]["metadata"] = metadata
    
    return job