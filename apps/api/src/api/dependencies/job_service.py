"""
Dependency injection for job service.
Provides IJobService implementation to API endpoints.
"""

from typing import Generator
from sqlalchemy.orm import Session
from fastapi import Depends

from ...db.base import get_db
from ...core.interfaces.job_service import IJobService
from ...services.job_service_adapter import JobServiceAdapter
from ...infrastructure.queue_factory import get_queue_publisher


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
    # Get queue publisher (uses factory to get appropriate implementation)
    queue_publisher = get_queue_publisher()
    
    # Return adapter wrapping the legacy service
    # In the future, this could return different implementations
    # based on configuration or environment
    return JobServiceAdapter(db, queue_publisher)


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