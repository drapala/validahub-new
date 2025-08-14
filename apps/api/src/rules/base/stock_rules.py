"""
Stock Validation Rules
Rules specific for stock/inventory fields
"""
from typing import Any, Optional
from src.core.interfaces import IRule, ValidationContext, ValidationError, Severity


class StockQuantityRule(IRule):
    """Combined rule for stock quantity - must be integer and non-negative"""
    
    def __init__(self, field: str, rule_id: str = None):
        super().__init__(rule_id or f"stock_quantity_{field}")
        self.field = field
    
    def can_apply(self, context: ValidationContext) -> bool:
        """Apply to specified field"""
        return context.column_name == self.field
    
    def validate(self, value: Any, context: ValidationContext) -> Optional[ValidationError]:
        """Check if value is a valid stock quantity"""
        if value is None:
            return None
        
        # First check if it's a valid number format
        try:
            num_value = float(value)
        except (ValueError, TypeError):
            return ValidationError(
                row=context.row_index,
                column=context.column_name,
                error="Invalid stock format",
                value=str(value),
                suggestion="Use integer value for stock",
                severity=Severity.ERROR,
                rule_id=self.rule_id
            )
        
        # Check if it's an integer
        if num_value != int(num_value):
            return ValidationError(
                row=context.row_index,
                column=context.column_name,
                error="Stock must be a whole number",
                value=str(value),
                suggestion="Use integer value for stock",
                severity=Severity.ERROR,
                rule_id=self.rule_id
            )
        
        # Check if it's non-negative
        if num_value < 0:
            return ValidationError(
                row=context.row_index,
                column=context.column_name,
                error="Stock cannot be negative",
                value=str(value),
                suggestion="Set stock to 0 or positive value",
                severity=Severity.ERROR,
                rule_id=self.rule_id
            )
        
        return None