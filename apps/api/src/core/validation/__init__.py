"""
Validation module with pluggable type validators.

The registry is initialized with built-in validators when the MELI ACL module
is imported. This avoids circular imports while maintaining modularity.
"""

from .registry import validation_registry, ValidatorSpec, ValidatorFn

__all__ = [
    'validation_registry',
    'ValidatorSpec', 
    'ValidatorFn',
]

# Note: Built-in validators are registered by the MELI ACL module to avoid circular imports
# See: src/adapters/acl_meli/__init__.py