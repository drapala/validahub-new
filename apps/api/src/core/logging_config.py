"""Generic logging utilities used across the project.

This module provides only framework-agnostic pieces: filters, formatters and
helpers for working with loggers. Infrastructure specific handlers and loggers
live in ``infrastructure.logging_config``.
"""

import logging
import logging.config
import json
from datetime import datetime, timezone
import contextvars
from typing import Dict, Any, Optional

# Shared context variable for correlation ID
correlation_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "correlation_id", default=None
)


class CorrelationFilter(logging.Filter):
    """Add correlation ID to log records."""

    def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        record.correlation_id = correlation_id_var.get() or "no-correlation-id"
        return True


class JSONFormatter(logging.Formatter):
    """Format logs as JSON for structured logging."""

    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", None),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
                "exc_info",
                "exc_text",
                "correlation_id",
            ]:
                log_obj[key] = value

        return json.dumps(log_obj)


def get_base_config() -> Dict[str, Any]:
    """Return base logging configuration with filters and formatters."""

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "correlation": {
                "()": CorrelationFilter,
            },
        },
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(module)s:%(funcName)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "()": JSONFormatter,
            },
        },
    }


def setup_logging(config: Dict[str, Any], log_level: Optional[str] = None) -> None:
    """Apply logging configuration.

    Args:
        config: Full logging configuration dictionary.
        log_level: Optional override for all logger levels.
    """

    if log_level:
        for logger_config in config.get("loggers", {}).values():
            if "level" in logger_config:
                logger_config["level"] = log_level
        if "root" in config and "level" in config["root"]:
            config["root"]["level"] = log_level

    logging.config.dictConfig(config)
    disable_noisy_loggers()


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""

    return logging.getLogger(name)


def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID for the current context."""

    correlation_id_var.set(correlation_id)


def get_correlation_id() -> Optional[str]:
    """Get correlation ID from the current context."""

    return correlation_id_var.get()


def disable_noisy_loggers() -> None:
    """Disable or reduce verbosity of noisy third-party loggers."""

    noisy_loggers = [
        "urllib3.connectionpool",
        "urllib3.poolmanager",
        "botocore.credentials",
        "botocore.hooks",
        "botocore.loaders",
        "botocore.parsers",
        "boto3.resources.action",
        "boto3.resources.factory",
        "kafka.conn",
        "kafka.client",
        "kafka.metrics",
        "httpx._client",
        "httpcore._sync.connection_pool",
        "httpcore._sync.http11",
        "asyncio",
        "concurrent.futures",
        "multipart.multipart",
        "watchfiles.main",
    ]

    for logger_name in noisy_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

