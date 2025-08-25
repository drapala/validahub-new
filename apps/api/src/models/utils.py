"""
Utility functions for SQLAlchemy models.
"""

from typing import Dict, Any


def get_table_args() -> Dict[str, Any]:
    """
    Get table arguments based on environment.
    
    In test environments, returns {'extend_existing': True} to allow
    model redefinition. In production, returns empty dict.
    
    Returns:
        Dictionary with table arguments
    """
    try:
        from src.test_settings import is_test_environment, BASE_MODEL_CONFIG
        if is_test_environment():
            return BASE_MODEL_CONFIG.get("__table_args__", {})
        return {}
    except ImportError:
        # If test_settings doesn't exist, we're in production
        return {}