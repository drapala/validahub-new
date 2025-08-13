"""
Common validation rules that can be reused across marketplaces
"""
import re
from typing import Any, Optional
from src.core.interfaces.rule import IRule, ValidationError, ValidationContext, Severity
import pandas as pd


class RequiredFieldRule(IRule):
    """Check if a required field is not empty"""
    
    def validate(self, value: Any, context: ValidationContext) -> Optional[ValidationError]:
        if pd.isna(value) or (isinstance(value, str) and not value.strip()):
            return ValidationError(
                row=context.row_number,
                column=context.column_name,
                error=f"Required field is empty",
                value=None,
                suggestion="Provide a value for this required field",
                severity=Severity.ERROR
            )
        return None


class MaxLengthRule(IRule):
    """Check if text doesn't exceed maximum length"""
    
    def __init__(self, max_length: int, error_msg: str = None):
        self.max_length = max_length
        self.error_msg = error_msg
    
    def validate(self, value: Any, context: ValidationContext) -> Optional[ValidationError]:
        if pd.notna(value) and len(str(value)) > self.max_length:
            return ValidationError(
                row=context.row_number,
                column=context.column_name,
                error=self.error_msg or f"Text is too long (max {self.max_length} characters)",
                value=str(value),
                suggestion=f"Truncate to {self.max_length} characters",
                severity=Severity.ERROR
            )
        return None


class MinLengthRule(IRule):
    """Check if text meets minimum length"""
    
    def __init__(self, min_length: int, error_msg: str = None):
        self.min_length = min_length
        self.error_msg = error_msg
    
    def validate(self, value: Any, context: ValidationContext) -> Optional[ValidationError]:
        if pd.notna(value) and len(str(value)) < self.min_length:
            return ValidationError(
                row=context.row_number,
                column=context.column_name,
                error=self.error_msg or f"Text is too short (min {self.min_length} characters)",
                value=str(value),
                suggestion=f"Expand to at least {self.min_length} characters",
                severity=Severity.ERROR
            )
        return None


class RegexRule(IRule):
    """Validate value matches a regex pattern"""
    
    def __init__(self, pattern: str, error_msg: str):
        self.pattern = re.compile(pattern)
        self.error_msg = error_msg
    
    def validate(self, value: Any, context: ValidationContext) -> Optional[ValidationError]:
        if pd.notna(value) and not self.pattern.match(str(value)):
            return ValidationError(
                row=context.row_number,
                column=context.column_name,
                error=self.error_msg,
                value=str(value),
                suggestion="Fix format to match expected pattern",
                severity=Severity.ERROR
            )
        return None


class URLRule(IRule):
    """Validate URL format"""
    
    def __init__(self, error_msg: str = None):
        self.error_msg = error_msg
        self.url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    def validate(self, value: Any, context: ValidationContext) -> Optional[ValidationError]:
        if pd.notna(value) and not self.url_pattern.match(str(value)):
            return ValidationError(
                row=context.row_number,
                column=context.column_name,
                error=self.error_msg or "Invalid URL format",
                value=str(value),
                suggestion="Use format: https://example.com",
                severity=Severity.ERROR
            )
        return None


class ImageURLRule(IRule):
    """Validate image URL format"""
    
    def __init__(self, error_msg: str = None):
        self.error_msg = error_msg
        self.url_rule = URLRule()
    
    def validate(self, value: Any, context: ValidationContext) -> Optional[ValidationError]:
        # First check if it's a valid URL
        url_error = self.url_rule.validate(value, context)
        if url_error:
            return url_error
        
        # Check if it has an image extension
        valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')
        if pd.notna(value) and not str(value).lower().endswith(valid_extensions):
            return ValidationError(
                row=context.row_number,
                column=context.column_name,
                error=self.error_msg or "URL must point to an image file",
                value=str(value),
                suggestion="Use image URL ending in .jpg, .png, etc.",
                severity=Severity.WARNING
            )
        return None


class EnumRule(IRule):
    """Validate value is in allowed list"""
    
    def __init__(self, allowed_values: list, error_msg: str = None):
        self.allowed_values = allowed_values
        self.error_msg = error_msg
    
    def validate(self, value: Any, context: ValidationContext) -> Optional[ValidationError]:
        if pd.notna(value) and str(value) not in self.allowed_values:
            return ValidationError(
                row=context.row_number,
                column=context.column_name,
                error=self.error_msg or f"Value must be one of: {', '.join(self.allowed_values)}",
                value=str(value),
                suggestion=f"Use one of: {', '.join(self.allowed_values)}",
                severity=Severity.ERROR
            )
        return None


class NumericRangeRule(IRule):
    """Validate numeric value is within range"""
    
    def __init__(self, min_value: float = None, max_value: float = None, error_msg: str = None):
        self.min_value = min_value
        self.max_value = max_value
        self.error_msg = error_msg
    
    def validate(self, value: Any, context: ValidationContext) -> Optional[ValidationError]:
        if pd.isna(value):
            return None
        
        try:
            num_value = float(value)
            
            if self.min_value is not None and num_value < self.min_value:
                return ValidationError(
                    row=context.row_number,
                    column=context.column_name,
                    error=self.error_msg or f"Value must be at least {self.min_value}",
                    value=str(value),
                    suggestion=f"Use value >= {self.min_value}",
                    severity=Severity.ERROR
                )
            
            if self.max_value is not None and num_value > self.max_value:
                return ValidationError(
                    row=context.row_number,
                    column=context.column_name,
                    error=self.error_msg or f"Value must be at most {self.max_value}",
                    value=str(value),
                    suggestion=f"Use value <= {self.max_value}",
                    severity=Severity.ERROR
                )
                
        except (ValueError, TypeError):
            return ValidationError(
                row=context.row_number,
                column=context.column_name,
                error="Value must be numeric",
                value=str(value),
                suggestion="Use a valid number",
                severity=Severity.ERROR
            )
        
        return None


class PositiveNumberRule(IRule):
    """Validate number is positive"""
    
    def validate(self, value: Any, context: ValidationContext) -> Optional[ValidationError]:
        if pd.isna(value):
            return None
        
        try:
            num_value = float(value)
            if num_value < 0:
                return ValidationError(
                    row=context.row_number,
                    column=context.column_name,
                    error="Value cannot be negative",
                    value=str(value),
                    suggestion="Use a positive number",
                    severity=Severity.ERROR
                )
        except (ValueError, TypeError):
            return ValidationError(
                row=context.row_number,
                column=context.column_name,
                error="Value must be numeric",
                value=str(value),
                suggestion="Use a valid number",
                severity=Severity.ERROR
            )
        
        return None


class IntegerRule(IRule):
    """Validate value is an integer"""
    
    def validate(self, value: Any, context: ValidationContext) -> Optional[ValidationError]:
        if pd.isna(value):
            return None
        
        try:
            float_val = float(value)
            if float_val != int(float_val):
                return ValidationError(
                    row=context.row_number,
                    column=context.column_name,
                    error="Value must be a whole number",
                    value=str(value),
                    suggestion="Use a whole number without decimals",
                    severity=Severity.ERROR
                )
        except (ValueError, TypeError):
            return ValidationError(
                row=context.row_number,
                column=context.column_name,
                error="Value must be numeric",
                value=str(value),
                suggestion="Use a valid whole number",
                severity=Severity.ERROR
            )
        
        return None


class StockQuantityRule(IRule):
    """Combined rule for stock quantity: must be non-negative integer"""
    
    def validate(self, value: Any, context: ValidationContext) -> Optional[ValidationError]:
        if pd.isna(value):
            return None
        
        try:
            float_val = float(value)
            
            # Check if it's an integer
            if float_val != int(float_val):
                return ValidationError(
                    row=context.row_number,
                    column=context.column_name,
                    error="Stock quantity must be a whole number",
                    value=str(value),
                    suggestion="Use a whole number without decimals",
                    severity=Severity.ERROR
                )
            
            # Check if it's non-negative
            if float_val < 0:
                return ValidationError(
                    row=context.row_number,
                    column=context.column_name,
                    error="Stock quantity cannot be negative",
                    value=str(value),
                    suggestion="Use 0 or a positive number",
                    severity=Severity.ERROR
                )
                
        except (ValueError, TypeError):
            return ValidationError(
                row=context.row_number,
                column=context.column_name,
                error="Stock quantity must be numeric",
                value=str(value),
                suggestion="Use a valid whole number",
                severity=Severity.ERROR
            )
        
        return None