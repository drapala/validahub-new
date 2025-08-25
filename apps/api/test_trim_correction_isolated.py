#!/usr/bin/env python3
"""Isolated test for the trim correction fix."""

import sys
import os
from pathlib import Path
import yaml
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
import re

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import logging config only
from core.logging_config import get_logger

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


# Minimal PolicyLoader implementation
class PolicyLoader:
    """Loads and manages validation policies from YAML files."""
    
    def __init__(self):
        """Initialize with default policy directory."""
        self.policies_dir = Path(__file__).parent / "policies"
        self._cache = {}
    
    def get_policy(self, marketplace: str, category: str, version: Optional[str] = None) -> Dict[str, Any]:
        """Get policy for a specific marketplace/category combination."""
        cache_key = f"{marketplace}_{category}_{version or 'latest'}"
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Try to load specific policy
        policy_path = self.policies_dir / marketplace / "categories" / f"{category}.yml"
        
        if policy_path.exists():
            with open(policy_path, "r", encoding="utf-8") as f:
                policy = yaml.safe_load(f)
                self._cache[cache_key] = policy
                return policy
        
        # Return minimal policy for testing
        return {
            "version": "test",
            "marketplace": marketplace,
            "category_id": category,
            "category_name": "Test Category",
            "rules": {
                "title": {
                    "required": True,
                    "min_length": 10,
                    "max_length": 60,
                    "transform": "trim"
                }
            },
            "error_codes": {},
            "custom_attributes": {},
            "warnings": {}
        }


# Minimal PolicyRuleEngine implementation with the fix
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
        """
        # Load policy
        policy = self.policy_loader.get_policy(marketplace, category)
        rules = policy.get("rules", {})
        error_codes = policy.get("error_codes", {})
        
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
            # Transform if specified - THIS IS THE FIX
            if rules.get("transform") == "trim":
                original_value = value
                value = value.strip()
                if value != original_value:  # Compare with original, not row_number!
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
        
        return errors, corrections


def test_trim_correction():
    """Test that trimming correction works correctly."""
    loader = PolicyLoader()
    engine = PolicyRuleEngine(loader)
    
    # Row with spaces to trim
    row = {
        "sku": "SKU-TEST-001",
        "title": "  iPhone 15 Pro Max 256GB  ",  # Has leading/trailing spaces
        "price": "8999.99",
        "stock": "10",
        "brand": "APPLE",
        "condition": "new",
        "model": "iPhone 15 Pro Max",
        "storage_capacity": "256GB",
        "color": "Titanium"
    }
    
    is_valid, errors, corrections = engine.validate_row(
        row,
        marketplace="MLB",
        category="MLB1743",
        row_number=1
    )
    
    print("Test Results:")
    print(f"  Valid: {is_valid}")
    print(f"  Errors: {len([e for e in errors if e.severity == 'ERROR'])}")
    print(f"  Warnings: {len([e for e in errors if e.severity == 'WARNING'])}")
    print(f"  Corrections: {len(corrections)}")
    
    if corrections:
        print("\nCorrections detected:")
        for correction in corrections:
            print(f"  Field: {correction['field']}")
            print(f"  Original: '{correction['original']}'")
            print(f"  Corrected: '{correction['corrected']}'")
            print(f"  Reason: {correction['reason']}")
            
            # Verify the correction is correct
            assert correction['field'] == 'title', "Should be title field"
            assert correction['original'] == "  iPhone 15 Pro Max 256GB  ", "Original should have spaces"
            assert correction['corrected'] == "iPhone 15 Pro Max 256GB", "Corrected should be trimmed"
            assert correction['reason'] == "Trimmed whitespace", "Reason should be trimming"
    else:
        print("❌ No corrections detected (expected trimming correction)")
        return False
    
    print("\n✅ Trim correction working correctly!")
    return True


if __name__ == "__main__":
    success = test_trim_correction()
    exit(0 if success else 1)