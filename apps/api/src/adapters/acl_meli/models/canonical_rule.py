"""
Canonical Rule Model (CRM) for marketplace rules.
This model represents the normalized format for all marketplace rules.
"""

from enum import Enum
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator
from core.validation import validation_registry


class RuleType(str, Enum):
    """Type of validation rule."""
    REQUIRED = "required"
    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    PATTERN = "pattern"
    ENUM = "enum"
    MIN_VALUE = "min_value"
    MAX_VALUE = "max_value"
    CUSTOM = "custom"
    DATE_FORMAT = "date_format"
    CONDITIONAL = "conditional"


class DataType(str, Enum):
    """Data types supported by rules."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    ARRAY = "array"
    OBJECT = "object"


class RuleSeverity(str, Enum):
    """Severity level of rule violations."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class RuleCondition(BaseModel):
    """Condition for conditional rules."""
    field: str = Field(..., description="Field to evaluate")
    operator: str = Field(..., description="Comparison operator (==, !=, >, <, >=, <=, in, not_in)")
    value: Any = Field(..., description="Value to compare against")
    
    @field_validator('operator')
    @classmethod
    def validate_operator(cls, v: str) -> str:
        valid_operators = ['==', '!=', '>', '<', '>=', '<=', 'in', 'not_in', 'contains', 'starts_with', 'ends_with']
        if v not in valid_operators:
            raise ValueError(f"Invalid operator: {v}. Must be one of {valid_operators}")
        return v


class CanonicalRule(BaseModel):
    """
    Canonical representation of a marketplace rule.
    This is the normalized format that all marketplace-specific rules are mapped to.
    """
    
    # Identification
    id: str = Field(..., description="Unique identifier for the rule")
    marketplace_id: str = Field(..., description="Source marketplace identifier (e.g., 'MELI', 'AMAZON')")
    original_id: str = Field(..., description="Original rule ID from the marketplace")
    
    # Rule definition
    field_name: str = Field(..., description="Field/attribute this rule applies to")
    rule_type: RuleType = Field(..., description="Type of validation rule")
    data_type: DataType = Field(..., description="Expected data type for the field")
    
    # Rule parameters
    params: Dict[str, Any] = Field(default_factory=dict, description="Rule-specific parameters")
    
    # Metadata
    severity: RuleSeverity = Field(default=RuleSeverity.ERROR, description="Severity of rule violation")
    message: Optional[str] = Field(None, description="Custom error message")
    description: Optional[str] = Field(None, description="Human-readable description of the rule")
    category: Optional[str] = Field(None, description="Rule category/group")
    tags: List[str] = Field(default_factory=list, description="Tags for rule classification")
    
    # Conditional logic
    condition: Optional[RuleCondition] = Field(None, description="Condition for applying this rule")
    depends_on: List[str] = Field(default_factory=list, description="Other field dependencies")
    
    # Versioning and lifecycle
    version: str = Field(default="1.0.0", description="Rule version")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Rule creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    is_active: bool = Field(default=True, description="Whether the rule is currently active")
    
    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional marketplace-specific metadata")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "id": "crm_rule_001",
                "marketplace_id": "MELI",
                "original_id": "meli_title_required",
                "field_name": "title",
                "rule_type": "required",
                "data_type": "string",
                "params": {},
                "severity": "error",
                "message": "Title is required",
                "description": "Product title must be provided",
                "category": "product_info",
                "tags": ["mandatory", "product"],
                "version": "1.0.0",
                "is_active": True
            }
        }
    
    def validate_value(self, value: Any) -> tuple[bool, Optional[str]]:
        """
        Validate a value against this rule.
        
        Args:
            value: Value to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # First check REQUIRED rule before type checking
            if self.rule_type == RuleType.REQUIRED:
                # Check for None, empty string, empty list, empty dict
                if value is None or value == "":
                    is_valid = False
                elif isinstance(value, (list, dict)) and len(value) == 0:
                    is_valid = False
                else:
                    is_valid = True
                return is_valid, None if is_valid else (self.message or f"{self.field_name} is required")
            
            # Skip type validation for None values (handled by REQUIRED rule)
            if value is None:
                # For non-required fields, None is valid for most rules except MIN_*
                if self.rule_type in [RuleType.MIN_LENGTH, RuleType.MIN_VALUE]:
                    return False, self.message or f"{self.field_name} cannot be empty"
                return True, None
            
            # Validate data type before applying rule
            if not self._validate_data_type(value):
                return False, f"{self.field_name} must be of type {self.data_type.value}"
            
            if self.rule_type == RuleType.MIN_LENGTH:
                min_len = self.params.get("min_length", 0)
                # Handle None separately from empty string
                if value is None:
                    return False, self.message or f"{self.field_name} must have at least {min_len} characters"
                is_valid = len(str(value)) >= min_len
                return is_valid, None if is_valid else (self.message or f"{self.field_name} must have at least {min_len} characters")
            
            elif self.rule_type == RuleType.MAX_LENGTH:
                max_len = self.params.get("max_length", float('inf'))
                # None is considered valid for max_length
                if value is None:
                    return True, None
                is_valid = len(str(value)) <= max_len
                return is_valid, None if is_valid else (self.message or f"{self.field_name} must have at most {max_len} characters")
            
            elif self.rule_type == RuleType.PATTERN:
                import re
                pattern = self.params.get("pattern", ".*")
                # Handle None separately
                if value is None:
                    return False, self.message or f"{self.field_name} does not match required pattern"
                # Use fullmatch to ensure entire string matches pattern
                is_valid = bool(re.fullmatch(pattern, str(value)))
                return is_valid, None if is_valid else (self.message or f"{self.field_name} does not match required pattern")
            
            elif self.rule_type == RuleType.ENUM:
                allowed_values = self.params.get("values", [])
                
                # Handle object-style allowed values (e.g., [{"id": "X", "name": "Y"}])
                if allowed_values and isinstance(allowed_values[0], dict):
                    # Check if value matches any object's 'id' field
                    valid_ids = [item.get("id") for item in allowed_values if "id" in item]
                    is_valid = value in valid_ids
                    # For error message, show only the IDs
                    display_values = valid_ids
                else:
                    # Simple list of values
                    is_valid = value in allowed_values
                    display_values = allowed_values
                
                return is_valid, None if is_valid else (self.message or f"{self.field_name} must be one of: {display_values}")
            
            elif self.rule_type == RuleType.MIN_VALUE:
                min_val = self.params.get("min_value", float('-inf'))
                # Handle None separately, but allow 0 and other falsy numeric values
                if value is None:
                    return False, self.message or f"{self.field_name} must be at least {min_val}"
                is_valid = float(value) >= min_val
                return is_valid, None if is_valid else (self.message or f"{self.field_name} must be at least {min_val}")
            
            elif self.rule_type == RuleType.MAX_VALUE:
                max_val = self.params.get("max_value", float('inf'))
                # None is considered valid for max_value
                if value is None:
                    return True, None
                is_valid = float(value) <= max_val
                return is_valid, None if is_valid else (self.message or f"{self.field_name} must be at most {max_val}")
            
            elif self.rule_type == RuleType.CUSTOM:
                # Custom validation logic would be implemented here
                return True, None
            
            else:
                return True, None
                
        except Exception as e:
            return False, f"Validation error for {self.field_name}: {str(e)}"
    
    def _validate_data_type(self, value: Any) -> bool:
        """
        Validate that value matches expected data type using the central registry.
        
        Args:
            value: Value to check
            
        Returns:
            True if type matches, False otherwise
        """
        if value is None:
            return True  # None is handled separately
        
        return validation_registry.validate(self.data_type, value)


class CanonicalRuleSet(BaseModel):
    """Collection of canonical rules for a marketplace."""
    
    marketplace_id: str = Field(..., description="Marketplace identifier")
    name: str = Field(..., description="Rule set name")
    version: str = Field(..., description="Rule set version")
    rules: List[CanonicalRule] = Field(default_factory=list, description="List of rules")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def get_rules_for_field(self, field_name: str) -> List[CanonicalRule]:
        """Get all rules that apply to a specific field."""
        return [rule for rule in self.rules if rule.field_name == field_name]
    
    def get_rules_by_type(self, rule_type: RuleType) -> List[CanonicalRule]:
        """Get all rules of a specific type."""
        return [rule for rule in self.rules if rule.rule_type == rule_type]
    
    def get_required_fields(self) -> List[str]:
        """Get list of all required fields."""
        return list(set(
            rule.field_name 
            for rule in self.rules 
            if rule.rule_type == RuleType.REQUIRED
        ))
    
    def validate_data(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Validate data against all rules in the set.
        
        Args:
            data: Data to validate
            
        Returns:
            Dictionary of field_name -> list of error messages
        """
        errors = {}
        required_fields = self.get_required_fields()
        missing_required_fields = set()
        
        # First pass: check for missing required fields
        for field in required_fields:
            value = data.get(field)
            if value is None or value == "" or (isinstance(value, (list, dict)) and len(value) == 0):
                missing_required_fields.add(field)
        
        for rule in self.rules:
            if not rule.is_active:
                continue
                
            field_value = data.get(rule.field_name)
            
            # Skip non-REQUIRED rules for missing required fields to avoid redundant errors
            if rule.field_name in missing_required_fields and rule.rule_type != RuleType.REQUIRED:
                continue
            
            # Skip non-required rules for missing values
            if field_value is None and rule.field_name not in required_fields:
                # Only REQUIRED rules should validate None values for optional fields
                if rule.rule_type != RuleType.REQUIRED:
                    continue
            
            is_valid, error_msg = rule.validate_value(field_value)
            
            if not is_valid and error_msg:
                if rule.field_name not in errors:
                    errors[rule.field_name] = []
                errors[rule.field_name].append(error_msg)
        
        return errors
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
