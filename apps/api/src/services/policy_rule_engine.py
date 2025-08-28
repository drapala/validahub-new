"""
Policy-based Rule Engine - Validates data using YAML policies.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from src.core.logging_config import get_logger
from .policy_loader import PolicyLoader

logger = get_logger(__name__)


class ValidationError:
    """Represents a validation error."""
    
    def __init__(self, field: str, code: str, message: str, value: Any = None, severity: str = "ERROR"):
        self.field = field
        self.code = code
        self.message = message
        self.value = value
        self.severity = severity
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "field": self.field,
            "code": self.code,
            "message": self.message,
            "value": str(self.value) if self.value is not None else None,
            "severity": self.severity
        }


class PolicyRuleEngine:
    """Executes validation rules from policies."""
    
    def __init__(self, policy_loader: Optional[PolicyLoader] = None):
        """Initialize with policy loader."""
        self.policy_loader = policy_loader or PolicyLoader()
    
    def validate_row(
        self, 
        row: Dict[str, Any], 
        marketplace: str, 
        category: str,
        row_number: int = 1
    ) -> Tuple[bool, List[ValidationError], List[Dict[str, Any]]]:
        """
        Validate a single row against policy rules.
        
        Args:
            row: Data row as dictionary
            marketplace: Marketplace code
            category: Category ID
            row_number: Row number for error reporting
            
        Returns:
            Tuple of (is_valid, errors, corrections)
        """
        # Load policy
        policy = self.policy_loader.get_policy(marketplace, category)
        rules = policy.get("rules", {})
        error_codes = policy.get("error_codes", {})
        custom_attributes = policy.get("custom_attributes", {})
        
        errors = []
        corrections = []
        
        # Validate standard fields
        for field_name, field_rules in rules.items():
            if not isinstance(field_rules, dict):
                continue
            
            value = row.get(field_name)
            field_errors, field_corrections = self._validate_field(
                field_name, value, field_rules, error_codes, row_number
            )
            errors.extend(field_errors)
            corrections.extend(field_corrections)
        
        # Validate custom attributes
        for attr_name, attr_rules in custom_attributes.items():
            # Custom attributes might have different column names
            value = row.get(attr_name.lower()) or row.get(attr_name)
            
            if attr_rules.get("required") and not value:
                errors.append(ValidationError(
                    field=attr_name,
                    code=f"{marketplace}_{attr_name}_REQUIRED",
                    message=error_codes.get(
                        f"{marketplace}_{attr_name}_REQUIRED",
                        f"{attr_name} is required"
                    ),
                    value=value
                ))
            elif value:
                # Validate based on type
                attr_errors = self._validate_custom_attribute(
                    attr_name, value, attr_rules, error_codes, marketplace
                )
                errors.extend(attr_errors)
        
        # Check for warnings (non-blocking)
        warnings = self._check_warnings(row, policy)
        for warning in warnings:
            warning.severity = "WARNING"
        errors.extend(warnings)
        
        # Determine if row is valid (only ERROR severity blocks)
        is_valid = not any(e.severity == "ERROR" for e in errors)
        
        return is_valid, errors, corrections
    
    def _validate_field(
        self,
        field_name: str,
        value: Any,
        rules: Dict[str, Any],
        error_codes: Dict[str, str],
        row_number: int
    ) -> Tuple[List[ValidationError], List[Dict[str, Any]]]:
        """Validate a single field against its rules."""
        errors = []
        corrections = []
        
        # Check required
        if rules.get("required") and not value:
            errors.append(ValidationError(
                field=field_name,
                code=f"{field_name.upper()}_REQUIRED",
                message=error_codes.get(
                    f"{field_name.upper()}_REQUIRED",
                    f"{field_name} is required"
                ),
                value=value
            ))
            return errors, corrections
        
        # Skip further validation if value is empty and not required
        if not value:
            return errors, corrections
        
        # String validations
        if isinstance(value, str):
            # Transform if specified
            if rules.get("transform") == "trim":
                original_value = value
                value = value.strip()
                if value != original_value:
                    corrections.append({
                        "field": field_name,
                        "original": original_value,
                        "corrected": value,
                        "reason": "Trimmed whitespace"
                    })
            
            # Length validation
            if "min_length" in rules and len(value) < rules["min_length"]:
                errors.append(ValidationError(
                    field=field_name,
                    code=f"{field_name.upper()}_TOO_SHORT",
                    message=f"{field_name} must be at least {rules['min_length']} characters",
                    value=value
                ))
            
            if "max_length" in rules and len(value) > rules["max_length"]:
                errors.append(ValidationError(
                    field=field_name,
                    code=f"{field_name.upper()}_TOO_LONG",
                    message=f"{field_name} cannot exceed {rules['max_length']} characters",
                    value=value
                ))
            
            # Forbidden characters
            if "forbidden_chars" in rules:
                for char in rules["forbidden_chars"]:
                    if char in value:
                        errors.append(ValidationError(
                            field=field_name,
                            code=f"{field_name.upper()}_FORBIDDEN_CHARS",
                            message=f"{field_name} contains forbidden character: {char}",
                            value=value
                        ))
                        break
            
            # Pattern validation
            if "pattern" in rules:
                if not re.match(rules["pattern"], value):
                    errors.append(ValidationError(
                        field=field_name,
                        code=f"{field_name.upper()}_INVALID_FORMAT",
                        message=f"{field_name} has invalid format",
                        value=value
                    ))
        
        # Numeric validations
        try:
            numeric_value = None
            if field_name in ["price", "stock"]:
                # Try to convert to number
                if isinstance(value, str):
                    # Handle Brazilian decimal format (comma)
                    value = value.replace(",", ".")
                numeric_value = float(value) if field_name == "price" else int(float(value))
                
                if "min_value" in rules and numeric_value < rules["min_value"]:
                    errors.append(ValidationError(
                        field=field_name,
                        code=f"{field_name.upper()}_TOO_LOW",
                        message=f"{field_name} must be at least {rules['min_value']}",
                        value=value
                    ))
                
                if "max_value" in rules and numeric_value > rules["max_value"]:
                    errors.append(ValidationError(
                        field=field_name,
                        code=f"{field_name.upper()}_TOO_HIGH",
                        message=f"{field_name} cannot exceed {rules['max_value']}",
                        value=value
                    ))
                
                # Check decimal places for price
                if field_name == "price" and "decimal_places" in rules:
                    decimal_str = str(numeric_value).split(".")
                    if len(decimal_str) > 1 and len(decimal_str[1]) > rules["decimal_places"]:
                        errors.append(ValidationError(
                            field=field_name,
                            code="PRICE_DECIMAL_PLACES",
                            message=f"Price cannot have more than {rules['decimal_places']} decimal places",
                            value=value
                        ))
        except (ValueError, TypeError):
            if field_name in ["price", "stock"]:
                errors.append(ValidationError(
                    field=field_name,
                    code=f"{field_name.upper()}_NOT_NUMERIC",
                    message=f"{field_name} must be numeric",
                    value=value
                ))
        
        # Enum validation
        if "enum_values" in rules:
            # Case-insensitive comparison if specified
            enum_values = rules["enum_values"]
            if not rules.get("case_sensitive", True):
                value_lower = str(value).lower()
                enum_values_lower = [v.lower() for v in enum_values]
                if value_lower not in enum_values_lower:
                    errors.append(ValidationError(
                        field=field_name,
                        code=f"{field_name.upper()}_INVALID_VALUE",
                        message=f"{field_name} must be one of: {', '.join(rules['enum_values'])}",
                        value=value
                    ))
            else:
                if value not in enum_values:
                    errors.append(ValidationError(
                        field=field_name,
                        code=f"{field_name.upper()}_INVALID_VALUE",
                        message=f"{field_name} must be one of: {', '.join(enum_values)}",
                        value=value
                    ))
        
        return errors, corrections
    
    def _validate_custom_attribute(
        self,
        attr_name: str,
        value: Any,
        rules: Dict[str, Any],
        error_codes: Dict[str, str],
        marketplace: str
    ) -> List[ValidationError]:
        """Validate custom attribute based on its type."""
        errors = []
        
        attr_type = rules.get("type", "string")
        
        if attr_type == "enum" and "values" in rules:
            if str(value) not in rules["values"]:
                errors.append(ValidationError(
                    field=attr_name,
                    code=f"{marketplace}_{attr_name}_INVALID",
                    message=f"{attr_name} must be one of: {', '.join(rules['values'])}",
                    value=value
                ))
        
        elif attr_type == "string":
            if "max_length" in rules and len(str(value)) > rules["max_length"]:
                errors.append(ValidationError(
                    field=attr_name,
                    code=f"{marketplace}_{attr_name}_TOO_LONG",
                    message=f"{attr_name} cannot exceed {rules['max_length']} characters",
                    value=value
                ))
            
            if "pattern" in rules and not re.match(rules["pattern"], str(value)):
                errors.append(ValidationError(
                    field=attr_name,
                    code=f"{marketplace}_{attr_name}_INVALID_FORMAT",
                    message=f"{attr_name} has invalid format",
                    value=value
                ))
        
        elif attr_type == "boolean":
            valid_bool_values = ["true", "false", "1", "0", "yes", "no", "sim", "não"]
            if str(value).lower() not in valid_bool_values:
                errors.append(ValidationError(
                    field=attr_name,
                    code=f"{marketplace}_{attr_name}_INVALID_BOOL",
                    message=f"{attr_name} must be a boolean value",
                    value=value
                ))
        
        return errors
    
    def _check_warnings(self, row: Dict[str, Any], policy: Dict[str, Any]) -> List[ValidationError]:
        """Check for non-blocking warnings."""
        warnings = []
        warning_messages = policy.get("warnings", {})
        
        # Check for missing recommended fields
        if not row.get("description"):
            warnings.append(ValidationError(
                field="description",
                code="DESCRIPTION_MISSING",
                message=warning_messages.get(
                    "DESCRIPTION_MISSING",
                    "Description improves conversion"
                ),
                value=None,
                severity="WARNING"
            ))
        
        # Check for low image count
        image_count = sum(1 for i in range(1, 11) if row.get(f"image_url_{i}"))
        if image_count < 3:
            warnings.append(ValidationError(
                field="images",
                code="LOW_IMAGE_COUNT",
                message=warning_messages.get(
                    "LOW_IMAGE_COUNT",
                    f"Only {image_count} image(s). More images improve conversion"
                ),
                value=image_count,
                severity="WARNING"
            ))
        
        return warnings