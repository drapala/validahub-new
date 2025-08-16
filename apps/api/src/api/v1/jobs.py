"""
Job queue API endpoints.
"""

import logging
from typing import Optional
from uuid import UUID
from fastapi import (
    APIRouter, Depends, HTTPException, Header, 
    status, Response, Query, Request
)
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.services.job_service import JobService
from src.schemas.job import (
    JobCreate, JobOut, JobResultOut, 
    JobListQuery, JobListResponse
)
from src.api.dependencies import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


def get_correlation_id(
    x_correlation_id: Optional[str] = Header(None, alias="X-Correlation-Id")
) -> Optional[str]:
    """Extract correlation ID from headers."""
    return x_correlation_id


def get_prefer_header(
    prefer: Optional[str] = Header(None)
) -> bool:
    """Check if client prefers representation on conflict."""
    return prefer == "return=representation" if prefer else False


@router.post(
    "",
    response_model=JobOut,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        202: {"description": "Job accepted for processing"},
        409: {"description": "Job with idempotency_key already exists"},
        500: {"description": "Failed to queue job"}
    }
)
async def create_job(
    job_data: JobCreate,
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
    correlation_id: Optional[str] = Depends(get_correlation_id),
    prefer_representation: bool = Depends(get_prefer_header)
):
    """
    Create a new async job.
    
    Features:
    - Idempotency via idempotency_key parameter
    - Queue routing based on user plan
    - Priority levels (1-10)
    - Correlation ID propagation
    
    If idempotency_key is provided and a job already exists:
    - Returns 409 if job is in progress (unless Prefer: return=representation)
    - Returns existing job if completed or with Prefer header
    """
    
    service = JobService(db)
    
    try:
        job, is_new = service.create_job(
            user_id=user_id,
            job_data=job_data,
            correlation_id=correlation_id,
            prefer_representation=prefer_representation
        )
        
        # Set Location header
        response.headers["Location"] = f"/api/v1/jobs/{job.id}"
        
        # Set correlation ID in response
        if correlation_id:
            response.headers["X-Correlation-Id"] = correlation_id
        
        # If returning existing job due to idempotency, use 200
        if not is_new:
            response.status_code = status.HTTP_200_OK
            logger.info(f"Returned existing job {job.id} for idempotency_key")
        
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating job: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/{job_id}",
    response_model=JobOut,
    responses={
        200: {"description": "Job details"},
        404: {"description": "Job not found"}
    }
)
async def get_job_status(
    job_id: UUID,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
    correlation_id: Optional[str] = Depends(get_correlation_id)
):
    """
    Get job status and details.
    
    Automatically syncs with Celery for active jobs.
    """
    
    service = JobService(db)
    
    try:
        job = service.get_job(str(job_id), user_id)
        return job
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job {job_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/{job_id}/result",
    response_model=JobResultOut,
    responses={
        200: {"description": "Job result"},
        404: {"description": "Job not found"},
        409: {"description": "Job not completed"}
    }
)
async def get_job_result(
    job_id: UUID,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
    correlation_id: Optional[str] = Depends(get_correlation_id)
):
    """
    Get job result.
    
    Returns result only if job status is SUCCEEDED.
    Result can be either:
    - result_ref: URI to result file (S3, etc)
    - result_json: Inline JSON for small results
    """
    
    service = JobService(db)
    
    try:
        result = service.get_job_result(str(job_id), user_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job result {job_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/{job_id}",
    response_model=JobOut,
    responses={
        200: {"description": "Job cancelled"},
        404: {"description": "Job not found"},
        409: {"description": "Cannot cancel job in terminal state"}
    }
)
async def cancel_job(
    job_id: UUID,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
    correlation_id: Optional[str] = Depends(get_correlation_id)
):
    """
    Cancel a job (best effort).
    
    Attempts to:
    1. Revoke task from Celery queue
    2. Mark job as CANCELLED in database
    
    Cannot cancel jobs that are already completed/failed/cancelled.
    """
    
    service = JobService(db)
    
    try:
        job = service.cancel_job(str(job_id), user_id)
        return job
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling job {job_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "",
    response_model=JobListResponse,
    responses={
        200: {"description": "List of jobs"}
    }
)
async def list_jobs(
    status: Optional[str] = Query(None, description="Filter by status"),
    task_name: Optional[str] = Query(None, description="Filter by task name"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    order_by: str = Query("created_at_desc", description="Sort order"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
    correlation_id: Optional[str] = Depends(get_correlation_id)
):
    """
    List jobs for current user.
    
    Features:
    - Filter by status, task_name
    - Pagination with limit/offset
    - Sorting by created_at
    
    Active jobs are automatically synced with Celery.
    """
    
    # Build query object
    from ...models.job import JobStatus
    
    # Validate and convert status with proper error handling
    job_status = None
    if status:
        try:
            job_status = JobStatus(status)
        except ValueError:
            allowed = [e.value for e in JobStatus]
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid status value '{status}'. Allowed values are: {allowed}"
            )
    
    query = JobListQuery(
        status=job_status,
        task_name=task_name,
        limit=limit,
        offset=offset,
        order_by=order_by
    )
    
    service = JobService(db)
    
    try:
        result = service.list_jobs(user_id, query)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing jobs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )