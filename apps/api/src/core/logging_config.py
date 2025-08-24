"""
Centralized logging configuration for ValidaHub API.
All logging setup should be done through this module.
"""

import logging
import logging.config
import sys
from typing import Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime

from .settings import get_settings


class CorrelationFilter(logging.Filter):
    """Add correlation ID to log records."""
    
    def filter(self, record):
        # Try to get correlation ID from context
        import contextvars
        correlation_id_var = contextvars.ContextVar('correlation_id', default=None)
        record.correlation_id = correlation_id_var.get() or 'no-correlation-id'
        return True


class JSONFormatter(logging.Formatter):
    """Format logs as JSON for structured logging."""
    
    def format(self, record):
        log_obj = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'correlation_id': getattr(record, 'correlation_id', None),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_obj['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 
                          'funcName', 'levelname', 'levelno', 'lineno', 
                          'module', 'msecs', 'message', 'pathname', 'process',
                          'processName', 'relativeCreated', 'stack_info', 
                          'thread', 'threadName', 'exc_info', 'exc_text',
                          'correlation_id']:
                log_obj[key] = value
        
        return json.dumps(log_obj)


def get_logging_config() -> Dict[str, Any]:
    """
    Get logging configuration based on environment.
    
    Returns:
        Dictionary with logging configuration
    """
    settings = get_settings()
    
    # Base configuration
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'correlation': {
                '()': CorrelationFilter,
            },
        },
        'formatters': {
            'default': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(module)s:%(funcName)s:%(lineno)d - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'json': {
                '()': JSONFormatter,
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'default',
                'stream': 'ext://sys.stdout',
                'filters': ['correlation'],
            },
            'console_detailed': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'detailed',
                'stream': 'ext://sys.stdout',
                'filters': ['correlation'],
            },
            'json_console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'json',
                'stream': 'ext://sys.stdout',
                'filters': ['correlation'],
            },
        },
        'loggers': {
            # Application loggers
            'src': {
                'level': settings.log_level.value,
                'handlers': ['console'],
                'propagate': False,
            },
            'apps': {
                'level': settings.log_level.value,
                'handlers': ['console'],
                'propagate': False,
            },
            
            # Third-party library loggers - set to WARNING or higher
            'uvicorn': {
                'level': 'INFO',
                'handlers': ['console'],
                'propagate': False,
            },
            'uvicorn.access': {
                'level': 'INFO',
                'handlers': ['console'],
                'propagate': False,
            },
            'uvicorn.error': {
                'level': 'INFO',
                'handlers': ['console'],
                'propagate': False,
            },
            'fastapi': {
                'level': 'INFO',
                'handlers': ['console'],
                'propagate': False,
            },
            'sqlalchemy': {
                'level': 'WARNING',
                'handlers': ['console'],
                'propagate': False,
            },
            'sqlalchemy.engine': {
                'level': 'WARNING',
                'handlers': ['console'],
                'propagate': False,
            },
            'celery': {
                'level': 'INFO',
                'handlers': ['console'],
                'propagate': False,
            },
            'redis': {
                'level': 'WARNING',
                'handlers': ['console'],
                'propagate': False,
            },
            'kafka': {
                'level': 'WARNING',
                'handlers': ['console'],
                'propagate': False,
            },
            'botocore': {
                'level': 'WARNING',
                'handlers': ['console'],
                'propagate': False,
            },
            'boto3': {
                'level': 'WARNING',
                'handlers': ['console'],
                'propagate': False,
            },
            'urllib3': {
                'level': 'WARNING',
                'handlers': ['console'],
                'propagate': False,
            },
            'httpx': {
                'level': 'WARNING',
                'handlers': ['console'],
                'propagate': False,
            },
            'httpcore': {
                'level': 'WARNING',
                'handlers': ['console'],
                'propagate': False,
            },
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console'],
        },
    }
    
    # Environment-specific adjustments
    if settings.environment.value == 'production':
        # Use JSON formatter in production
        config['loggers']['src']['handlers'] = ['json_console']
        config['loggers']['apps']['handlers'] = ['json_console']
        config['root']['handlers'] = ['json_console']
        
        # Set stricter log levels
        config['loggers']['uvicorn']['level'] = 'WARNING'
        config['loggers']['uvicorn.access']['level'] = 'WARNING'
        
    elif settings.environment.value == 'development':
        # Use detailed formatter in development
        config['loggers']['src']['handlers'] = ['console_detailed']
        config['loggers']['apps']['handlers'] = ['console_detailed']
        
        # Enable SQL logging in development if needed
        if settings.database.echo:
            config['loggers']['sqlalchemy.engine']['level'] = 'INFO'
    
    return config


def setup_logging(
    config: Optional[Dict[str, Any]] = None,
    log_level: Optional[str] = None
) -> None:
    """
    Setup logging configuration.
    
    This should be called once at application startup.
    
    Args:
        config: Optional custom logging configuration
        log_level: Optional override for log level
    """
    if config is None:
        config = get_logging_config()
    
    # Apply log level override if provided
    if log_level:
        for logger_config in config['loggers'].values():
            if 'level' in logger_config:
                logger_config['level'] = log_level
        config['root']['level'] = log_level
    
    # Apply configuration
    logging.config.dictConfig(config)
    
    # Log the configuration
    logger = logging.getLogger(__name__)
    settings = get_settings()
    logger.info(
        f"Logging configured for {settings.environment.value} environment "
        f"with log level {settings.log_level.value}"
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    
    This is the preferred way to get loggers in the application.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def set_correlation_id(correlation_id: str) -> None:
    """
    Set correlation ID for the current context.
    
    Args:
        correlation_id: Correlation ID to set
    """
    import contextvars
    correlation_id_var = contextvars.ContextVar('correlation_id', default=None)
    correlation_id_var.set(correlation_id)


def get_correlation_id() -> Optional[str]:
    """
    Get correlation ID from the current context.
    
    Returns:
        Current correlation ID or None
    """
    import contextvars
    correlation_id_var = contextvars.ContextVar('correlation_id', default=None)
    return correlation_id_var.get()


# Disable noisy loggers by default
def disable_noisy_loggers():
    """Disable or reduce verbosity of noisy third-party loggers."""
    noisy_loggers = [
        'urllib3.connectionpool',
        'urllib3.poolmanager',
        'botocore.credentials',
        'botocore.hooks',
        'botocore.loaders',
        'botocore.parsers',
        'boto3.resources.action',
        'boto3.resources.factory',
        'kafka.conn',
        'kafka.client',
        'kafka.metrics',
        'httpx._client',
        'httpcore._sync.connection_pool',
        'httpcore._sync.http11',
        'asyncio',
        'concurrent.futures',
        'multipart.multipart',
        'watchfiles.main',
    ]
    
    for logger_name in noisy_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


# Call this after setup_logging
disable_noisy_loggers()