"""
Services module.

Exports all service classes for easy import.
"""

# Legacy services (will be deprecated)
from .job_service import JobService
from .csv_validation_service import CSVValidationService as CsvValidationService
from .rule_engine_service import RuleEngineService
from .storage_service import StorageService

# Refactored services (SOLID principle)
from .job_creation_service import JobCreationService
from .job_query_service import JobQueryService
from .job_cancellation_service import JobCancellationService
from .job_status_sync_service import JobStatusSyncService
from .job_idempotency_service import JobIdempotencyService
from .job_service_refactored import JobServiceRefactored

# Adapters
from .job_service_adapter import JobServiceAdapter
# from .rule_engine_service_adapter import RuleEngineServiceAdapter  # Class is RuleEngineService

__all__ = [
    # Legacy
    "JobService",
    "CsvValidationService",
    "RuleEngineService",
    "StorageService",
    
    # Refactored
    "JobCreationService",
    "JobQueryService",
    "JobCancellationService",
    "JobStatusSyncService",
    "JobIdempotencyService",
    "JobServiceRefactored",
    
    # Adapters
    "JobServiceAdapter",
    # "RuleEngineServiceAdapter",  # Class is RuleEngineService
]