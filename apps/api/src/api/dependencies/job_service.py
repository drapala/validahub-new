"""
Dependency injection for job service.
Provides IJobService implementation to API endpoints.
"""

from typing import Generator, Optional
from sqlalchemy.orm import Session
from fastapi import Depends

from ...db.base import get_db
from ...core.interfaces.job_service import IJobService
from ...services.job_service_adapter import JobServiceAdapter
from ...services.job_creation_service import JobCreationService
from ...services.job_query_service import JobQueryService
from ...core.validators.job_validator import JobValidator
from ...infrastructure.repositories.job_repository import JobRepository
from ...infrastructure.queue_factory import get_queue_publisher

# Singleton instances for stateless services
_job_validator_instance: Optional[JobValidator] = None
_queue_publisher_instance: Optional[object] = None


def _get_job_validator_singleton() -> JobValidator:
    """Get singleton instance of JobValidator."""
    global _job_validator_instance
    if _job_validator_instance is None:
        _job_validator_instance = JobValidator()
    return _job_validator_instance


def _get_queue_publisher_singleton():
    """Get singleton instance of queue publisher."""
    global _queue_publisher_instance
    if _queue_publisher_instance is None:
        _queue_publisher_instance = get_queue_publisher()
    return _queue_publisher_instance


def get_job_service(db: Session = Depends(get_db)) -> IJobService:
    """
    Get job service instance.
    
    This factory function provides the IJobService implementation
    to API endpoints via dependency injection.
    
    Args:
        db: Database session from dependency injection
        
    Returns:
        IJobService implementation (currently JobServiceAdapter)
    """
    # Get queue publisher singleton
    queue_publisher = _get_queue_publisher_singleton()
    
    # Return adapter wrapping the legacy service
    # In the future, this could return different implementations
    # based on configuration or environment
    return JobServiceAdapter(db, queue_publisher)


def get_job_repository(db: Session = Depends(get_db)) -> JobRepository:
    """Get job repository instance."""
    return JobRepository(db)


def get_job_validator() -> JobValidator:
    """Get job validator singleton instance."""
    return _get_job_validator_singleton()


def get_job_creation_service(
    db: Session = Depends(get_db)
) -> JobCreationService:
    """
    Get job creation service instance.
    
    Uses the refactored services following SOLID principles.
    """
    repository = get_job_repository(db)
    validator = _get_job_validator_singleton()
    queue_publisher = _get_queue_publisher_singleton()
    
    return JobCreationService(repository, validator, queue_publisher)


def get_job_query_service(
    db: Session = Depends(get_db)
) -> JobQueryService:
    """
    Get job query service instance.
    
    Uses the refactored services following SOLID principles.
    """
    repository = get_job_repository(db)
    queue_publisher = _get_queue_publisher_singleton()
    
    return JobQueryService(repository, queue_publisher)


def get_async_job_service(db: Session = Depends(get_db)) -> IJobService:
    """
    Get async-capable job service instance.
    
    This is a placeholder for future async implementations.
    Currently returns the same as get_job_service.
    
    Args:
        db: Database session from dependency injection
        
    Returns:
        IJobService implementation
    """
    return get_job_service(db)