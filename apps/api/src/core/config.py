"""
Configuration settings for the API application.
"""

import os
from typing import Set, Dict
from enum import Enum

class ValidationConfig:
    """Configuration for validation rules and settings."""
    
    # Allowed rulesets for validation (prevents path traversal attacks)
    ALLOWED_RULESETS: Set[str] = {
        "default",
        "strict", 
        "lenient",
        "minimal",
        "comprehensive"
    }
    
    # File size limits (in bytes)
    MAX_CSV_FILE_SIZE = int(os.getenv("MAX_CSV_FILE_SIZE", str(1 * 1024 * 1024 * 1024)))  # 1GB default
    STREAMING_THRESHOLD = int(os.getenv("STREAMING_THRESHOLD", str(100 * 1024 * 1024)))  # 100MB default
    
    @classmethod
    def get_allowed_rulesets(cls) -> Set[str]:
        """
        Get allowed rulesets from environment or use defaults.
        
        Environment variable format: ALLOWED_RULESETS=default,strict,custom
        """
        env_rulesets = os.getenv("ALLOWED_RULESETS")
        if env_rulesets:
            return set(ruleset.strip() for ruleset in env_rulesets.split(","))
        return cls.ALLOWED_RULESETS
    
    @classmethod
    def is_valid_ruleset(cls, ruleset: str) -> bool:
        """Check if a ruleset is valid."""
        return ruleset in cls.get_allowed_rulesets()


class JobPlan(str, Enum):
    """Job subscription plans."""
    FREE = "free"
    PRO = "pro"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class QueueConfig:
    """Configuration for queue and task mappings."""
    
    # Queue mapping by plan
    QUEUE_BY_PLAN: Dict[JobPlan, str] = {
        JobPlan.FREE: "queue:free",
        JobPlan.PRO: "queue:pro",
        JobPlan.BUSINESS: "queue:business",
        JobPlan.ENTERPRISE: "queue:enterprise"
    }
    
    # Valid task names (used for validation)
    VALID_TASKS: Set[str] = {
        "validate_csv_job",
        "correct_csv_job",
        "analyze_data_job",
        "export_results_job",
        "sync_connector_job",
        "generate_report_job"
    }
    
    # Task name mappings to full Celery task paths
    TASK_MAPPINGS: Dict[str, str] = {
        "validate_csv_job": "src.workers.tasks.validate_csv_job",
        "correct_csv_job": "src.workers.tasks.correct_csv_job",
        "sync_connector_job": "src.workers.tasks.sync_connector_job",
        "generate_report_job": "src.workers.tasks.generate_report_job"
    }
    
    # Celery task time limits (in seconds)
    VALIDATE_CSV_JOB_TIME_LIMIT = int(os.getenv("VALIDATE_CSV_JOB_TIME_LIMIT", "300"))
    VALIDATE_CSV_JOB_SOFT_TIME_LIMIT = int(os.getenv("VALIDATE_CSV_JOB_SOFT_TIME_LIMIT", "270"))
    
    CORRECT_CSV_JOB_TIME_LIMIT = int(os.getenv("CORRECT_CSV_JOB_TIME_LIMIT", "600"))
    CORRECT_CSV_JOB_SOFT_TIME_LIMIT = int(os.getenv("CORRECT_CSV_JOB_SOFT_TIME_LIMIT", "570"))
    
    DEFAULT_JOB_TIME_LIMIT = int(os.getenv("DEFAULT_JOB_TIME_LIMIT", "300"))
    DEFAULT_JOB_SOFT_TIME_LIMIT = int(os.getenv("DEFAULT_JOB_SOFT_TIME_LIMIT", "270"))
    
    @classmethod
    def get_task_mappings(cls) -> Dict[str, str]:
        """
        Get task mappings from environment or use defaults.
        
        Environment variable format: TASK_MAPPINGS=task1:path1,task2:path2
        """
        env_mappings = os.getenv("TASK_MAPPINGS")
        if env_mappings:
            mappings = {}
            for mapping in env_mappings.split(","):
                if ":" in mapping:
                    task, path = mapping.strip().split(":", 1)
                    mappings[task] = path
            return mappings if mappings else cls.TASK_MAPPINGS
        return cls.TASK_MAPPINGS
    
    @classmethod
    def get_celery_task_name(cls, task_name: str) -> str:
        """Get the full Celery task path for a given task name."""
        mappings = cls.get_task_mappings()
        return mappings.get(task_name, f"src.workers.tasks.{task_name}")
    
    @classmethod
    def get_queue_for_plan(cls, plan: JobPlan) -> str:
        """Get queue name for a subscription plan."""
        return cls.QUEUE_BY_PLAN.get(plan, "queue:free")
    
    @classmethod
    def get_valid_tasks(cls) -> Set[str]:
        """Get valid task names from configuration."""
        env_tasks = os.getenv("VALID_TASKS")
        if env_tasks:
            return set(task.strip() for task in env_tasks.split(","))
        return cls.VALID_TASKS