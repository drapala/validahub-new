"""
Base Correction Implementations
Reusable corrections that can be used across different marketplaces
"""
import re
from typing import Any, Dict, Optional
from src.core.interfaces.corrector import ICorrection
from src.core.interfaces.rule import ValidationError


class TruncateCorrection(ICorrection):
    """Truncate strings that are too long"""
    
    def __init__(self, max_length: int):
        self.max_length = max_length
    
    def can_correct(self, error: ValidationError) -> bool:
        return "too long" in error.error.lower() or "exceeds maximum" in error.error.lower()
    
    def apply(self, value: Any, error: ValidationError, context: Dict[str, Any]) -> Any:
        if value is None:
            return ""
        return str(value)[:self.max_length]
    
    def get_priority(self) -> int:
        return 10


class DefaultValueCorrection(ICorrection):
    """Provide default value for empty required fields"""
    
    def __init__(self, default_value: Any):
        self.default_value = default_value
    
    def can_correct(self, error: ValidationError) -> bool:
        return "required" in error.error.lower() and "empty" in error.error.lower()
    
    def apply(self, value: Any, error: ValidationError, context: Dict[str, Any]) -> Any:
        if value is None or (isinstance(value, str) and not value.strip()):
            return self.default_value
        return value
    
    def get_priority(self) -> int:
        return 20


class MinValueCorrection(ICorrection):
    """Set minimum value for numeric fields"""
    
    def __init__(self, min_value: float):
        self.min_value = min_value
    
    def can_correct(self, error: ValidationError) -> bool:
        return any(phrase in error.error.lower() for phrase in [
            "must be greater than",
            "cannot be negative",
            "minimum value",
            "too small"
        ])
    
    def apply(self, value: Any, error: ValidationError, context: Dict[str, Any]) -> Any:
        try:
            num_value = float(value) if value is not None else 0
            return max(num_value, self.min_value)
        except (ValueError, TypeError):
            return self.min_value
    
    def get_priority(self) -> int:
        return 30


class MaxValueCorrection(ICorrection):
    """Set maximum value for numeric fields"""
    
    def __init__(self, max_value: float):
        self.max_value = max_value
    
    def can_correct(self, error: ValidationError) -> bool:
        return any(phrase in error.error.lower() for phrase in [
            "must be less than",
            "exceeds maximum",
            "too large",
            "maximum value"
        ])
    
    def apply(self, value: Any, error: ValidationError, context: Dict[str, Any]) -> Any:
        try:
            num_value = float(value) if value is not None else 0
            return min(num_value, self.max_value)
        except (ValueError, TypeError):
            return self.max_value
    
    def get_priority(self) -> int:
        return 30


class RegexCleanCorrection(ICorrection):
    """Clean values to match regex pattern"""
    
    def __init__(self, pattern: str, replacement: str = ""):
        self.pattern = re.compile(pattern)
        self.replacement = replacement
    
    def can_correct(self, error: ValidationError) -> bool:
        return "invalid format" in error.error.lower() or "must match" in error.error.lower()
    
    def apply(self, value: Any, error: ValidationError, context: Dict[str, Any]) -> Any:
        if value is None:
            return ""
        # Remove characters that don't match the pattern
        cleaned = re.sub(r'[^A-Z0-9\-_]', '', str(value).upper())
        return cleaned if cleaned else f"AUTO-{context.get('row', 1)}"
    
    def get_priority(self) -> int:
        return 40


class CaseCorrection(ICorrection):
    """Fix case issues (upper, lower, title)"""
    
    def __init__(self, case_type: str = "upper"):
        self.case_type = case_type
    
    def can_correct(self, error: ValidationError) -> bool:
        return any(phrase in error.error.lower() for phrase in [
            "must be uppercase",
            "must be lowercase",
            "case",
            "capitalization"
        ])
    
    def apply(self, value: Any, error: ValidationError, context: Dict[str, Any]) -> Any:
        if value is None:
            return ""
        str_value = str(value)
        
        if self.case_type == "upper":
            return str_value.upper()
        elif self.case_type == "lower":
            return str_value.lower()
        elif self.case_type == "title":
            return str_value.title()
        return str_value
    
    def get_priority(self) -> int:
        return 50


class NumericCleanCorrection(ICorrection):
    """Extract numeric value from string"""
    
    def __init__(self, default: float = 0):
        self.default = default
    
    def can_correct(self, error: ValidationError) -> bool:
        return any(phrase in error.error.lower() for phrase in [
            "must be numeric",
            "invalid number",
            "not a number",
            "must be integer"
        ])
    
    def apply(self, value: Any, error: ValidationError, context: Dict[str, Any]) -> Any:
        if value is None:
            return self.default
        
        # Try direct conversion first
        try:
            return float(value)
        except (ValueError, TypeError):
            # Extract digits from string
            str_value = str(value)
            digits = ''.join(filter(lambda x: x.isdigit() or x == '.', str_value))
            if digits:
                try:
                    return float(digits)
                except ValueError:
                    pass
        
        return self.default
    
    def get_priority(self) -> int:
        return 35


class AutoGenerateCorrection(ICorrection):
    """Auto-generate values for fields like SKU"""
    
    def __init__(self, prefix: str = "AUTO", field_type: str = "sku"):
        self.prefix = prefix
        self.field_type = field_type
    
    def can_correct(self, error: ValidationError) -> bool:
        return ("required" in error.error.lower() and 
                self.field_type.lower() in error.column.lower())
    
    def apply(self, value: Any, error: ValidationError, context: Dict[str, Any]) -> Any:
        if value and str(value).strip():
            return value
        
        row = context.get('row', 1)
        if self.field_type == "sku":
            return f"{self.prefix}-SKU-{row:04d}"
        elif self.field_type == "id":
            return f"{self.prefix}-ID-{row:04d}"
        else:
            return f"{self.prefix}-{row:04d}"
    
    def get_priority(self) -> int:
        return 25