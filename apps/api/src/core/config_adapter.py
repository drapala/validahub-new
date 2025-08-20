"""
Adapter for existing config classes to use new Pydantic settings.
Provides backward compatibility during migration.
"""

from typing import Set, Dict
from .settings import get_settings, JobPlan


class ValidationConfig:
    """Adapter for validation configuration."""
    
    @classmethod
    def get_allowed_rulesets(cls) -> Set[str]:
        """Get allowed rulesets from settings."""
        return get_settings().validation.allowed_rulesets
    
    @classmethod
    def is_valid_ruleset(cls, ruleset: str) -> bool:
        """Check if a ruleset is valid."""
        return ruleset in cls.get_allowed_rulesets()
    
    @property
    def MAX_CSV_FILE_SIZE(self) -> int:
        """Get max CSV file size."""
        return get_settings().validation.max_csv_file_size
    
    @property
    def STREAMING_THRESHOLD(self) -> int:
        """Get streaming threshold."""
        return get_settings().validation.streaming_threshold


class QueueConfig:
    """Adapter for queue configuration."""
    
    @classmethod
    def get_valid_tasks(cls) -> Set[str]:
        """Get valid task names from settings."""
        return get_settings().queue.valid_tasks
    
    @classmethod
    def get_task_mappings(cls) -> Dict[str, str]:
        """Get task mappings from settings."""
        return get_settings().queue.task_mappings
    
    @classmethod
    def get_celery_task_name(cls, task_name: str) -> str:
        """Get the full Celery task path for a given task name."""
        mappings = cls.get_task_mappings()
        return mappings.get(task_name, f"src.workers.tasks.{task_name}")
    
    @classmethod
    def get_queue_for_plan(cls, plan: JobPlan) -> str:
        """Get queue name for a subscription plan."""
        return get_settings().queue.queue_by_plan.get(plan, "queue:free")