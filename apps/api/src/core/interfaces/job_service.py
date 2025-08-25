"""
Interface for job service implementations.
This allows different job queue backends while maintaining a consistent API.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from enum import Enum

from schemas.job import (
    JobCreate, 
    JobOut, 
    JobResultOut,
    JobListQuery, 
    JobListResponse,
    JobStatusUpdate
)


class JobStatus(str, Enum):
    """Job status enumeration."""
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class IJobService(ABC):
    """
    Interface for job service implementations.
    
    This interface defines the contract for job management services,
    allowing different implementations (Celery, SQS, in-memory, etc.)
    while maintaining a consistent API.
    """
    
    @abstractmethod
    def create_job(
        self,
        user_id: str,
        job_data: JobCreate,
        correlation_id: Optional[str] = None,
        prefer_representation: bool = False
    ) -> Tuple[JobOut, bool]:
        """
        Create a new job with idempotency check.
        
        Args:
            user_id: User ID creating the job
            job_data: Job creation data
            correlation_id: Optional correlation ID for tracing
            prefer_representation: If True, return existing job on conflict
            
        Returns:
            Tuple of (JobOut, is_new) where is_new indicates if job was created
            
        Raises:
            ValueError: If job data is invalid
            HTTPException: If job creation fails
        """
        pass
    
    @abstractmethod
    def get_job(self, job_id: str, user_id: Optional[str] = None) -> Optional[JobOut]:
        """
        Get a job by ID.
        
        Args:
            job_id: Job ID to retrieve
            user_id: Optional user ID for authorization check
            
        Returns:
            JobOut if found, None otherwise
        """
        pass
    
    @abstractmethod
    def list_jobs(
        self,
        user_id: str,
        query: JobListQuery
    ) -> JobListResponse:
        """
        List jobs for a user with filtering and pagination.
        
        Args:
            user_id: User ID to list jobs for
            query: Query parameters for filtering and pagination
            
        Returns:
            JobListResponse with jobs and pagination info
        """
        pass
    
    @abstractmethod
    def cancel_job(
        self,
        job_id: str,
        user_id: Optional[str] = None,
        reason: Optional[str] = None
    ) -> bool:
        """
        Cancel a job.
        
        Args:
            job_id: Job ID to cancel
            user_id: Optional user ID for authorization check
            reason: Optional cancellation reason
            
        Returns:
            True if cancellation was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def update_job_status(
        self,
        job_id: str,
        status_update: JobStatusUpdate
    ) -> bool:
        """
        Update job status (typically called by workers).
        
        Args:
            job_id: Job ID to update
            status_update: Status update data
            
        Returns:
            True if update was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_job_result(
        self,
        job_id: str,
        user_id: Optional[str] = None
    ) -> Optional[JobResultOut]:
        """
        Get job result.
        
        Args:
            job_id: Job ID to get result for
            user_id: Optional user ID for authorization check
            
        Returns:
            JobResultOut if available, None otherwise
        """
        pass
    
    @abstractmethod
    def cleanup_old_jobs(
        self,
        older_than: datetime,
        status_filter: Optional[List[JobStatus]] = None
    ) -> int:
        """
        Clean up old jobs from the system.
        
        Args:
            older_than: Delete jobs older than this datetime
            status_filter: Optional list of statuses to filter by
            
        Returns:
            Number of jobs cleaned up
        """
        pass
    
    @abstractmethod
    def get_queue_stats(self) -> Dict[str, Any]:
        """
        Get queue statistics.
        
        Returns:
            Dictionary with queue statistics:
            - total_jobs: Total number of jobs
            - queued: Number of queued jobs
            - running: Number of running jobs
            - succeeded: Number of succeeded jobs
            - failed: Number of failed jobs
            - by_queue: Jobs per queue
            - by_task: Jobs per task type
        """
        pass
    
    @abstractmethod
    def retry_job(
        self,
        job_id: str,
        user_id: Optional[str] = None
    ) -> Tuple[JobOut, bool]:
        """
        Retry a failed job.
        
        Args:
            job_id: Job ID to retry
            user_id: Optional user ID for authorization check
            
        Returns:
            Tuple of (JobOut, success) where success indicates if retry was initiated
        """
        pass