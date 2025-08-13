"""
Required Fields Rule
Validates that required fields are present and not empty
"""
from typing import Any, Optional, List
from src.core.interfaces import IRule, ValidationContext, ValidationError, Severity


class RequiredFieldRule(IRule):
    """Rule to check if required fields are present"""
    
    def __init__(self, fields: List[str], rule_id: str = None):
        super().__init__(rule_id or "required_fields")
        self.required_fields = fields
    
    def can_apply(self, context: ValidationContext) -> bool:
        """This rule applies if the column is in required fields list"""
        return context.column_name in self.required_fields
    
    def validate(self, value: Any, context: ValidationContext) -> Optional[ValidationError]:
        """Check if value is present and not empty"""
        # Pandas pode representar valores vazios como NaN
        import pandas as pd
        if pd.isna(value) or value is None or (isinstance(value, str) and value.strip() == ""):
            return ValidationError(
                row=context.row_index,
                column=context.column_name,
                error="Required field is empty",
                value=value,
                suggestion=f"Provide value for {context.column_name}",
                severity=Severity.ERROR,
                rule_id=self.rule_id
            )
        return None