"""
Job validation logic separated from service layer.
Follows Single Responsibility Principle.
"""

import logging
import re
from typing import Optional, List, Set
from datetime import datetime

from ...schemas.job import JobCreate, JobPlan
from ...core.result import Result, Ok, Err, JobError
from ..config_adapter import ValidationConfig, QueueConfig
from ..constants import (
    PARAM_INPUT_URI,
    PARAM_MARKETPLACE,
    PARAM_CATEGORY,
    PARAM_ANALYSIS_TYPE,
    PARAM_JOB_ID,
    PARAM_FORMAT,
    PARAM_RULESET,
    DEFAULT_RULESET,
    MIN_PRIORITY,
    MAX_PRIORITY,
    MAX_RETRY_COUNT
)

logger = logging.getLogger(__name__)


class JobValidator:
    """
    Validates job-related data and business rules.
    
    This class is responsible only for validation logic,
    keeping it separate from business logic and data access.
    """
    
    def __init__(self):
        """Initialize the validator."""
        # Currently stateless, but keeps the interface consistent
        # for potential future initialization needs
        pass
    
    
    def validate_job_creation(self, job_data: JobCreate) -> Result[JobCreate, JobError]:
        """
        Validate job creation data.
        
        Args:
            job_data: Job creation data to validate
            
        Returns:
            Result with validated data or validation error
        """
        # Validate task name
        task_validation = self.validate_task_name(job_data.task)
        if task_validation.is_err():
            return task_validation
        
        # Validate priority
        priority_validation = self.validate_priority(job_data.priority)
        if priority_validation.is_err():
            return priority_validation
        
        # Validate ruleset for CSV tasks
        if job_data.task in ["validate_csv_job", "correct_csv_job"]:
            ruleset_validation = self.validate_ruleset(
                job_data.params.get(PARAM_RULESET, DEFAULT_RULESET)
            )
            if ruleset_validation.is_err():
                return ruleset_validation
        
        # Validate required parameters
        params_validation = self.validate_required_params(
            job_data.task,
            job_data.params
        )
        if params_validation.is_err():
            return params_validation
        
        return Ok(job_data)
    
    def validate_task_name(self, task_name: str) -> Result[str, JobError]:
        """
        Validate task name.
        
        Args:
            task_name: Task name to validate
            
        Returns:
            Result with task name or validation error
        """
        if not task_name:
            logger.warning("Empty task name provided")
            return Err(JobError.VALIDATION_ERROR)
        
        # Get valid tasks from configuration
        valid_tasks = QueueConfig.get_valid_tasks()
        if task_name not in valid_tasks:
            logger.warning(f"Invalid task name: {task_name}")
            return Err(JobError.VALIDATION_ERROR)
        
        return Ok(task_name)
    
    def validate_priority(self, priority: int) -> Result[int, JobError]:
        """
        Validate job priority.
        
        Args:
            priority: Priority value (1-10)
            
        Returns:
            Result with priority or validation error
        """
        if priority < MIN_PRIORITY or priority > MAX_PRIORITY:
            logger.warning(f"Invalid priority: {priority}")
            return Err(JobError.VALIDATION_ERROR)
        
        return Ok(priority)
    
    def validate_ruleset(self, ruleset: str) -> Result[str, JobError]:
        """
        Validate ruleset name for CSV validation tasks.
        
        Args:
            ruleset: Ruleset name
            
        Returns:
            Result with ruleset or validation error
        """
        if not ValidationConfig.is_valid_ruleset(ruleset):
            allowed = ValidationConfig.get_allowed_rulesets()
            logger.warning(f"Invalid ruleset '{ruleset}'. Allowed: {allowed}")
            return Err(JobError.VALIDATION_ERROR)
        
        return Ok(ruleset)
    
    def validate_required_params(
        self,
        task_name: str,
        params: dict
    ) -> Result[dict, JobError]:
        """
        Validate required parameters for a task.
        
        Args:
            task_name: Name of the task
            params: Parameters provided
            
        Returns:
            Result with params or validation error
        """
        required_params = self.get_required_params(task_name)
        
        missing = []
        for param in required_params:
            if param not in params or params[param] is None:
                missing.append(param)
        
        if missing:
            logger.warning(f"Missing required params for {task_name}: {missing}")
            return Err(JobError.VALIDATION_ERROR)
        
        return Ok(params)
    
    def get_required_params(self, task_name: str) -> List[str]:
        """
        Get required parameters for a task.
        
        Args:
            task_name: Name of the task
            
        Returns:
            List of required parameter names
        """
        task_params = {
            "validate_csv_job": [PARAM_INPUT_URI, PARAM_MARKETPLACE, PARAM_CATEGORY],
            "correct_csv_job": [PARAM_INPUT_URI, PARAM_MARKETPLACE, PARAM_CATEGORY],
            "analyze_data_job": [PARAM_INPUT_URI, PARAM_ANALYSIS_TYPE],
            "export_results_job": [PARAM_JOB_ID, PARAM_FORMAT]
        }
        
        return task_params.get(task_name, [])
    
    def get_queue_for_plan(self, plan: JobPlan) -> str:
        """
        Get queue name for a subscription plan.
        
        Args:
            plan: User's subscription plan
            
        Returns:
            Queue name
        """
        return QueueConfig.get_queue_for_plan(plan)
    
    def can_cancel_job(self, status: str) -> bool:
        """
        Check if a job can be cancelled based on its status.
        
        Args:
            status: Current job status
            
        Returns:
            True if job can be cancelled
        """
        cancellable_statuses = {"queued", "running", "retrying"}
        return status.lower() in cancellable_statuses
    
    def can_retry_job(self, status: str, retry_count: int, max_retries: int = MAX_RETRY_COUNT) -> bool:
        """
        Check if a job can be retried.
        
        Args:
            status: Current job status
            retry_count: Current retry count
            max_retries: Maximum allowed retries
            
        Returns:
            True if job can be retried
        """
        if status.lower() != "failed":
            return False
        
        if retry_count >= max_retries:
            return False
        
        return True
    
    def validate_idempotency_key(
        self,
        key: Optional[str]
    ) -> Result[Optional[str], JobError]:
        """
        Validate idempotency key format.
        
        Args:
            key: Idempotency key to validate
            
        Returns:
            Result with key or validation error
        """
        if key is None:
            return Ok(None)
        
        # Check length
        if len(key) < 8 or len(key) > 128:
            logger.warning(f"Invalid idempotency key length: {len(key)}")
            return Err(JobError.VALIDATION_ERROR)
        
        # Check format (alphanumeric + hyphen + underscore)
        if not re.match(r'^[a-zA-Z0-9_-]+$', key):
            logger.warning(f"Invalid idempotency key format: {key}")
            return Err(JobError.VALIDATION_ERROR)
        
        return Ok(key)