"""Infrastructure-specific logging configuration.

This module extends the generic logging configuration with handlers and
logger definitions for the frameworks used by the application (FastAPI,
Uvicorn, Celery, SQLAlchemy, etc.).
"""

from typing import Dict, Any, Optional

from src.core.logging_config import (
    get_base_config,
    setup_logging as core_setup_logging,
)
from src.core.settings import get_settings


def get_logging_config() -> Dict[str, Any]:
    """Build full logging configuration including handlers and loggers."""

    settings = get_settings()
    config = get_base_config()

    config.update(
        {
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG",
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                    "filters": ["correlation"],
                },
                "console_detailed": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG",
                    "formatter": "detailed",
                    "stream": "ext://sys.stdout",
                    "filters": ["correlation"],
                },
                "json_console": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG",
                    "formatter": "json",
                    "stream": "ext://sys.stdout",
                    "filters": ["correlation"],
                },
            },
            "loggers": {
                # Application loggers
                "src": {
                    "level": settings.log_level.value,
                    "handlers": ["console"],
                    "propagate": False,
                },
                "apps": {
                    "level": settings.log_level.value,
                    "handlers": ["console"],
                    "propagate": False,
                },
                # Framework loggers
                "uvicorn": {
                    "level": "INFO",
                    "handlers": ["console"],
                    "propagate": False,
                },
                "uvicorn.error": {
                    "level": "INFO",
                    "handlers": ["console"],
                    "propagate": False,
                },
                "uvicorn.access": {
                    "level": "INFO",
                    "handlers": ["console"],
                    "propagate": False,
                },
                "celery": {
                    "level": "INFO",
                    "handlers": ["console"],
                    "propagate": False,
                },
                "celery.task": {
                    "level": "INFO",
                    "handlers": ["console"],
                    "propagate": True,
                },
                "sqlalchemy.engine": {
                    "level": "WARNING",
                    "handlers": ["console"],
                    "propagate": False,
                },
            },
            "root": {
                "level": settings.log_level.value,
                "handlers": ["console"],
            },
        }
    )

    # Environment-specific adjustments
    if settings.environment.value == "production":
        config["loggers"]["src"]["handlers"] = ["json_console"]
        config["loggers"]["apps"]["handlers"] = ["json_console"]
        config["root"]["handlers"] = ["json_console"]

        config["loggers"]["uvicorn"]["level"] = "WARNING"
        config["loggers"]["uvicorn.access"]["level"] = "WARNING"

    elif settings.environment.value == "development":
        config["loggers"]["src"]["handlers"] = ["console_detailed"]
        config["loggers"]["apps"]["handlers"] = ["console_detailed"]

        if settings.database.echo:
            config["loggers"]["sqlalchemy.engine"]["level"] = "INFO"

    return config


def setup_logging(
    config: Optional[Dict[str, Any]] = None, log_level: Optional[str] = None
) -> None:
    """Configure logging using infrastructure defaults."""

    if config is None:
        config = get_logging_config()

    core_setup_logging(config=config, log_level=log_level)

