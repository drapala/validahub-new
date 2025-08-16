"""
API dependencies module.
"""

from .auth import (
    get_current_user_id,
    get_optional_user_id,
    require_admin_user
)

__all__ = [
    "get_current_user_id",
    "get_optional_user_id",
    "require_admin_user"
]