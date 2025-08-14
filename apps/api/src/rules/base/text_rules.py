"""
Text Validation Rules
Rules for validating text fields
"""
from typing import Any, Optional
from src.core.interfaces import IRule, ValidationContext, ValidationError, Severity


class TextLengthRule(IRule):
    """Rule to check text length constraints"""
    
    def __init__(self, field: str, max_length: int, min_length: int = 0, rule_id: str = None):
        super().__init__(rule_id or f"text_length_{field}")
        self.field = field
        self.max_length = max_length
        self.min_length = min_length
    
    def can_apply(self, context: ValidationContext) -> bool:
        """Apply to specified field"""
        return context.column_name == self.field
    
    def validate(self, value: Any, context: ValidationContext) -> Optional[ValidationError]:
        """Check text length"""
        if value is None:
            return None  # Let RequiredFieldRule handle None values
        
        text = str(value)
        length = len(text)
        
        if length > self.max_length:
            return ValidationError(
                row=context.row_index,
                column=context.column_name,
                error=f"Text too long (max {self.max_length} chars)",
                value=text[:50] + "..." if length > 50 else text,
                suggestion=f"Shorten to {self.max_length} characters",
                severity=Severity.ERROR,
                rule_id=self.rule_id
            )
        
        if length < self.min_length:
            return ValidationError(
                row=context.row_index,
                column=context.column_name,
                error=f"Text too short (min {self.min_length} chars)",
                value=text,
                suggestion=f"Expand to at least {self.min_length} characters",
                severity=Severity.ERROR,
                rule_id=self.rule_id
            )
        
        return None


class TextPatternRule(IRule):
    """Rule to validate text against regex pattern"""
    
    def __init__(self, field: str, pattern: str, error_msg: str, rule_id: str = None):
        super().__init__(rule_id or f"text_pattern_{field}")
        import re
        self.field = field
        self.pattern = re.compile(pattern)
        self.error_msg = error_msg
    
    def can_apply(self, context: ValidationContext) -> bool:
        """Apply to specified field"""
        return context.column_name == self.field
    
    def validate(self, value: Any, context: ValidationContext) -> Optional[ValidationError]:
        """Check if text matches pattern"""
        if value is None:
            return None
        
        text = str(value)
        if not self.pattern.match(text):
            return ValidationError(
                row=context.row_index,
                column=context.column_name,
                error=self.error_msg,
                value=text,
                suggestion="Fix format to match required pattern",
                severity=Severity.ERROR,
                rule_id=self.rule_id
            )
        
        return None