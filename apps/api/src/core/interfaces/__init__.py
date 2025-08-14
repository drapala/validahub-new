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
from .validator import (
    IValidator,
    IValidationPipeline
)
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
    # Corrector interfaces
    'ICorrection',
    'ICorrectionStrategy',
    'ICorrectionProvider',
]