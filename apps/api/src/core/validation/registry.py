"""
Validation registry for pluggable type validators.
Allows dynamic registration of validators without modifying core code.
"""

from __future__ import annotations
from typing import Any, Callable, Dict, Optional
from dataclasses import dataclass

ValidatorFn = Callable[[Any], bool]


@dataclass(frozen=True)
class ValidatorSpec:
    """Metadata for validators - useful for documentation and telemetry."""
    name: str
    description: Optional[str] = None


class ValidationRegistry:
    """
    Thread-safe registry for type validators.
    
    Features:
    - get() never raises: falls back to default validator
    - register() allows overriding (last registration wins)
    - Supports metadata for introspection
    """
    
    def __init__(self) -> None:
        self._validators: Dict[Any, ValidatorFn] = {}
        self._meta: Dict[Any, ValidatorSpec] = {}
        self._default: ValidatorFn = lambda v: True  # Permissive by default
    
    def set_default(self, fn: ValidatorFn) -> None:
        """Set the default validator for unknown types."""
        self._default = fn
    
    def register(
        self, 
        key: Any, 
        fn: ValidatorFn, 
        *, 
        meta: Optional[ValidatorSpec] = None
    ) -> None:
        """
        Register a validator for a specific key (usually an enum value).
        
        Args:
            key: The type key (e.g., DataType.STRING)
            fn: Validator function that returns True if valid
            meta: Optional metadata about the validator
        """
        self._validators[key] = fn
        if meta:
            self._meta[key] = meta
    
    def has(self, key: Any) -> bool:
        """Check if a validator is registered for the key."""
        return key in self._validators
    
    def validate(self, key: Any, value: Any) -> bool:
        """
        Validate a value using the registered validator for the key.
        Falls back to default validator if key not found.
        """
        fn = self._validators.get(key, self._default)
        return fn(value)
    
    def describe(self, key: Any) -> Optional[ValidatorSpec]:
        """Get metadata for a registered validator."""
        return self._meta.get(key)
    
    def list_validators(self) -> Dict[Any, ValidatorSpec]:
        """List all registered validators with their metadata."""
        return dict(self._meta)
    
    def clear(self) -> None:
        """Clear all registered validators (useful for testing)."""
        self._validators.clear()
        self._meta.clear()


# Global instance (can be injected/mocked in tests)
validation_registry = ValidationRegistry()