"""
Built-in validators for standard data types.
These cover the common types used across all marketplaces.
"""

from __future__ import annotations
from datetime import datetime, date
from typing import Any
from .registry import validation_registry, ValidatorSpec


def _is_int_without_bool(v: Any) -> bool:
    """Check if value is an integer but not a boolean."""
    return isinstance(v, int) and not isinstance(v, bool)


def _is_float_like_without_bool(v: Any) -> bool:
    """Check if value is float-like (float or int) but not a boolean."""
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def register_builtin_validators(DataType: Any) -> None:
    """
    Register standard validators for built-in DataTypes.
    
    Args:
        DataType: The DataType enum to use as keys
    """
    # String validation
    validation_registry.register(
        DataType.STRING,
        lambda v: isinstance(v, str),
        meta=ValidatorSpec(
            name="string",
            description="Accepts Python str"
        ),
    )
    
    # Integer validation (excludes bool)
    validation_registry.register(
        DataType.INTEGER,
        _is_int_without_bool,
        meta=ValidatorSpec(
            name="integer",
            description="Accepts int, rejects bool"
        ),
    )
    
    # Float validation (accepts int or float, excludes bool)
    validation_registry.register(
        DataType.FLOAT,
        _is_float_like_without_bool,
        meta=ValidatorSpec(
            name="float",
            description="Accepts float or int (not bool)"
        ),
    )
    
    # Boolean validation
    validation_registry.register(
        DataType.BOOLEAN,
        lambda v: isinstance(v, bool),
        meta=ValidatorSpec(
            name="boolean",
            description="Accepts bool"
        ),
    )
    
    # Date validation (accepts string or datetime/date objects)
    validation_registry.register(
        DataType.DATE,
        lambda v: isinstance(v, (str, datetime, date)),
        meta=ValidatorSpec(
            name="date",
            description="Accepts str, datetime, or date"
        ),
    )
    
    # DateTime validation
    validation_registry.register(
        DataType.DATETIME,
        lambda v: isinstance(v, (str, datetime)),
        meta=ValidatorSpec(
            name="datetime",
            description="Accepts str or datetime"
        ),
    )
    
    # Array validation
    validation_registry.register(
        DataType.ARRAY,
        lambda v: isinstance(v, (list, tuple)),
        meta=ValidatorSpec(
            name="array",
            description="Accepts list or tuple"
        ),
    )
    
    # Object validation
    validation_registry.register(
        DataType.OBJECT,
        lambda v: isinstance(v, dict),
        meta=ValidatorSpec(
            name="object",
            description="Accepts dict"
        ),
    )
    
    # Set permissive default (maintains current behavior)
    validation_registry.set_default(lambda v: True)