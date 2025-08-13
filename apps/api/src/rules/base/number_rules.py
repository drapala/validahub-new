"""
Number Validation Rules
Rules for validating numeric fields
"""
from typing import Any, Optional
from src.core.interfaces import IRule, ValidationContext, ValidationError, Severity


class NumberRangeRule(IRule):
    """Rule to check if number is within range"""
    
    def __init__(self, field: str, min_value: float = None, max_value: float = None, rule_id: str = None):
        super().__init__(rule_id or f"number_range_{field}")
        self.field = field
        self.min_value = min_value
        self.max_value = max_value
    
    def can_apply(self, context: ValidationContext) -> bool:
        """Apply to specified field"""
        return context.column_name == self.field
    
    def validate(self, value: Any, context: ValidationContext) -> Optional[ValidationError]:
        """Check if number is within range"""
        if value is None:
            return None
        
        try:
            num_value = float(value)
        except (ValueError, TypeError):
            return ValidationError(
                row=context.row_index,
                column=context.column_name,
                error="Invalid number format",
                value=str(value),
                suggestion="Use a valid number",
                severity=Severity.ERROR,
                rule_id=self.rule_id
            )
        
        if self.min_value is not None and num_value < self.min_value:
            return ValidationError(
                row=context.row_index,
                column=context.column_name,
                error=f"Value must be at least {self.min_value}",
                value=str(value),
                suggestion=f"Set value to {self.min_value} or higher",
                severity=Severity.ERROR,
                rule_id=self.rule_id
            )
        
        if self.max_value is not None and num_value > self.max_value:
            return ValidationError(
                row=context.row_index,
                column=context.column_name,
                error=f"Value must be at most {self.max_value}",
                value=str(value),
                suggestion=f"Set value to {self.max_value} or lower",
                severity=Severity.ERROR,
                rule_id=self.rule_id
            )
        
        return None


class PositiveNumberRule(IRule):
    """Rule to ensure number is positive"""
    
    def __init__(self, field: str, allow_zero: bool = False, rule_id: str = None):
        super().__init__(rule_id or f"positive_number_{field}")
        self.field = field
        self.allow_zero = allow_zero
    
    def can_apply(self, context: ValidationContext) -> bool:
        """Apply to specified field"""
        return context.column_name == self.field
    
    def validate(self, value: Any, context: ValidationContext) -> Optional[ValidationError]:
        """Check if number is positive"""
        if value is None:
            return None
        
        try:
            num_value = float(value)
        except (ValueError, TypeError):
            return ValidationError(
                row=context.row_index,
                column=context.column_name,
                error="Invalid number format",
                value=str(value),
                suggestion="Use a valid number",
                severity=Severity.ERROR,
                rule_id=self.rule_id
            )
        
        if self.allow_zero:
            if num_value < 0:
                return ValidationError(
                    row=context.row_index,
                    column=context.column_name,
                    error="Value cannot be negative",
                    value=str(value),
                    suggestion="Set to 0 or positive value",
                    severity=Severity.ERROR,
                    rule_id=self.rule_id
                )
        else:
            if num_value <= 0:
                return ValidationError(
                    row=context.row_index,
                    column=context.column_name,
                    error="Value must be greater than 0",
                    value=str(value),
                    suggestion="Set a positive value",
                    severity=Severity.ERROR,
                    rule_id=self.rule_id
                )
        
        return None


class IntegerRule(IRule):
    """Rule to ensure value is an integer"""
    
    def __init__(self, field: str, rule_id: str = None):
        super().__init__(rule_id or f"integer_{field}")
        self.field = field
    
    def can_apply(self, context: ValidationContext) -> bool:
        """Apply to specified field"""
        return context.column_name == self.field
    
    def validate(self, value: Any, context: ValidationContext) -> Optional[ValidationError]:
        """Check if value is an integer"""
        if value is None:
            return None
        
        try:
            # Try to convert to float first to handle numeric strings
            float_val = float(value)
            # Check if it's actually an integer
            if float_val != int(float_val):
                raise ValueError("Not an integer")
        except (ValueError, TypeError):
            return ValidationError(
                row=context.row_index,
                column=context.column_name,
                error="Value must be a whole number",
                value=str(value),
                suggestion="Use an integer value",
                severity=Severity.ERROR,
                rule_id=self.rule_id
            )
        
        return None