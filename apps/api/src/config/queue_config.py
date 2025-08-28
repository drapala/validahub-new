"""
Queue configuration loader.
Loads queue settings from external sources (YAML, env vars).
"""

import os
import yaml
from src.core.logging_config import get_logger
from typing import Dict, Any, Optional
from pathlib import Path

logger = get_logger(__name__)


class QueueConfig:
    """Manages queue configuration from external sources."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize with optional config file path.
        
        Args:
            config_path: Path to YAML config file
        """
        self.config_path = config_path or os.getenv(
            "QUEUE_CONFIG_PATH",
            "config/queue_config.yaml"
        )
        self._config: Dict[str, Any] = {}
        self._load_config()
        
    def _load_config(self):
        """Load configuration from file and environment."""
        
        # Try to load from YAML file
        if self.config_path and Path(self.config_path).exists():
            try:
                with open(self.config_path, 'r') as f:
                    self._config = yaml.safe_load(f)
                logger.info(f"Loaded queue config from {self.config_path}")
            except Exception as e:
                logger.error(f"Failed to load queue config: {e}")
                self._config = self._get_default_config()
        else:
            logger.warning(f"Queue config file not found at {self.config_path}, using defaults")
            self._config = self._get_default_config()
            
        # Override with environment variables
        self._apply_env_overrides()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "queues": {
                "default": {
                    "name": os.getenv("DEFAULT_QUEUE", "celery"),
                    "max_priority": 10
                },
                "free": {
                    "name": os.getenv("FREE_QUEUE", "queue:free"),
                    "max_priority": 5
                },
                "premium": {
                    "name": os.getenv("PREMIUM_QUEUE", "queue:premium"),
                    "max_priority": 10
                }
            },
            "task_routes": {
                "validate_csv_job": {
                    "queue": os.getenv("VALIDATE_QUEUE", "queue:free"),
                    "priority": 5,
                    "max_retries": 5
                },
                "correct_csv_job": {
                    "queue": os.getenv("CORRECT_QUEUE", "queue:free"),
                    "priority": 5,
                    "max_retries": 3
                },
                "sync_connector_job": {
                    "queue": os.getenv("SYNC_QUEUE", "queue:premium"),
                    "priority": 7,
                    "max_retries": 3
                },
                "generate_report_job": {
                    "queue": os.getenv("REPORT_QUEUE", "queue:free"),
                    "priority": 3,
                    "max_retries": 2
                }
            }
        }
        
    def _apply_env_overrides(self):
        """Apply environment variable overrides."""
        
        # Override specific queue names
        if os.getenv("QUEUE_PREFIX"):
            prefix = os.getenv("QUEUE_PREFIX")
            for queue_config in self._config.get("queues", {}).values():
                if "name" in queue_config:
                    queue_config["name"] = f"{prefix}:{queue_config['name']}"
                    
        # Override task routes from environment
        for task_name in self._config.get("task_routes", {}):
            env_var = f"TASK_QUEUE_{task_name.upper()}"
            if os.getenv(env_var):
                self._config["task_routes"][task_name]["queue"] = os.getenv(env_var)
                
    def get_queue_name(self, queue_key: str) -> str:
        """
        Get actual queue name for a queue key.
        
        Args:
            queue_key: Queue identifier (e.g., "free", "premium")
            
        Returns:
            Actual queue name to use
        """
        queue_config = self._config.get("queues", {}).get(queue_key, {})
        return queue_config.get("name", queue_key)
        
    def get_task_route(self, task_name: str) -> Dict[str, Any]:
        """
        Get routing configuration for a task.
        
        Args:
            task_name: Name of the task
            
        Returns:
            Task routing configuration
        """
        return self._config.get("task_routes", {}).get(
            task_name,
            {"queue": "celery", "priority": 5}
        )
        
    def get_celery_task_routes(self) -> Dict[str, Dict[str, Any]]:
        """
        Get Celery-compatible task routes dictionary.
        
        Returns:
            Dictionary mapping task names to routing options
        """
        routes = {}
        for task_name, config in self._config.get("task_routes", {}).items():
            routes[task_name] = {
                "queue": config.get("queue", "celery"),
                "routing_key": config.get("routing_key", task_name),
                "priority": config.get("priority", 5)
            }
        return routes
        
    def get_queue_tier(self, tier: str) -> Dict[str, Any]:
        """
        Get configuration for a queue tier.
        
        Args:
            tier: Tier name (e.g., "free", "premium")
            
        Returns:
            Tier configuration
        """
        return self._config.get("queue_tiers", {}).get(
            tier,
            {"queues": [], "rate_limit": None, "max_concurrent": 10}
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """Get full configuration as dictionary."""
        return self._config


# Global instance
_queue_config: Optional[QueueConfig] = None


def get_queue_config() -> QueueConfig:
    """Get or create global queue configuration."""
    global _queue_config
    if _queue_config is None:
        _queue_config = QueueConfig()
    return _queue_config