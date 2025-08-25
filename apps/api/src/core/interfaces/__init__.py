"""
Core Interfaces
Export all interface definitions
"""
from .rule import (
    IRule,
    ICompositeRule,
    IRuleProvider,
    IRuleRegistry,
    ValidationContext,
    ValidationError,
    Severity
)
from .validation import IValidator
from .validator import IValidationPipeline
from .rule_engine import IRuleEngineService
from .corrector import (
    ICorrection,
    ICorrectionStrategy,
    ICorrectionProvider
)

__all__ = [
    # Rule interfaces
    'IRule',
    'ICompositeRule',
    'IRuleProvider',
    'IRuleRegistry',
    'ValidationContext',
    'ValidationError',
    'Severity',
    # Validator interfaces
    'IValidator',
    'IValidationPipeline',
    # Rule engine interfaces
    'IRuleEngineService',
    # Corrector interfaces
    'ICorrection',
    'ICorrectionStrategy',
    'ICorrectionProvider',
]