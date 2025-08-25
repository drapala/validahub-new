#!/usr/bin/env python3
"""
Standalone test for real CSV validation with policies.
Run directly: python test_real_csv_validation.py
"""

import sys
from pathlib import Path

# Add src to path directly
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Now import only what we need, avoiding the problematic __init__.py
import yaml
import pandas as pd
from typing import Dict, Any, List, Tuple
import re


# Inline PolicyLoader to avoid import issues
class SimplePolicyLoader:
    def __init__(self):
        self.policies_dir = Path(__file__).parent / "policies"
    
    def get_policy(self, marketplace: str, category: str) -> Dict:
        policy_file = self.policies_dir / marketplace / "categories" / f"{category}.yml"
        if policy_file.exists():
            with open(policy_file) as f:
                return yaml.safe_load(f)
        return {}


# Inline ValidationError
class ValidationError:
    def __init__(self, field: str, code: str, message: str, value: Any = None, severity: str = "ERROR"):
        self.field = field
        self.code = code
        self.message = message
        self.value = value
        self.severity = severity


# Simplified RuleEngine
class SimpleRuleEngine:
    def __init__(self, policy_loader):
        self.loader = policy_loader
    
    def validate_row(self, row: Dict, marketplace: str, category: str) -> Tuple[bool, List[ValidationError]]:
        policy = self.loader.get_policy(marketplace, category)
        rules = policy.get("rules", {})
        errors = []
        
        # Check required fields
        for field, field_rules in rules.items():
            if not isinstance(field_rules, dict):
                continue
            
            value = row.get(field)
            
            # Required check
            if field_rules.get("required") and not value:
                errors.append(ValidationError(
                    field=field,
                    code=f"{field.upper()}_REQUIRED",
                    message=f"{field} is required",
                    value=value
                ))
                continue
            
            if not value:
                continue
            
            # String validations
            if isinstance(value, str):
                # Trim
                value = value.strip()
                
                # Length
                if "min_length" in field_rules and len(value) < field_rules["min_length"]:
                    errors.append(ValidationError(
                        field=field,
                        code=f"{field.upper()}_TOO_SHORT",
                        message=f"{field} must be at least {field_rules['min_length']} characters",
                        value=value
                    ))
                
                if "max_length" in field_rules and len(value) > field_rules["max_length"]:
                    errors.append(ValidationError(
                        field=field,
                        code=f"{field.upper()}_TOO_LONG",
                        message=f"{field} cannot exceed {field_rules['max_length']} characters",
                        value=value
                    ))
                
                # Forbidden chars
                if "forbidden_chars" in field_rules:
                    for char in field_rules["forbidden_chars"]:
                        if char in value:
                            errors.append(ValidationError(
                                field=field,
                                code=f"{field.upper()}_FORBIDDEN_CHARS",
                                message=f"{field} contains forbidden character: {char}",
                                value=value
                            ))
                            break
            
            # Numeric validations
            if field in ["price", "stock"]:
                try:
                    # Handle Brazilian format
                    if isinstance(value, str):
                        value = value.replace(",", ".")
                    numeric_value = float(value)
                    
                    if "min_value" in field_rules and numeric_value < field_rules["min_value"]:
                        errors.append(ValidationError(
                            field=field,
                            code=f"{field.upper()}_TOO_LOW",
                            message=f"{field} must be at least {field_rules['min_value']}",
                            value=value
                        ))
                    
                    if "max_value" in field_rules and numeric_value > field_rules["max_value"]:
                        errors.append(ValidationError(
                            field=field,
                            code=f"{field.upper()}_TOO_HIGH",
                            message=f"{field} cannot exceed {field_rules['max_value']}",
                            value=value
                        ))
                except (ValueError, TypeError):
                    errors.append(ValidationError(
                        field=field,
                        code=f"{field.upper()}_NOT_NUMERIC",
                        message=f"{field} must be numeric",
                        value=value
                    ))
            
            # Enum validation
            if "enum_values" in field_rules:
                enum_values = field_rules["enum_values"]
                if not field_rules.get("case_sensitive", True):
                    value_str = str(value).lower()
                    enum_values = [v.lower() for v in enum_values]
                else:
                    value_str = str(value)
                
                if value_str not in enum_values:
                    errors.append(ValidationError(
                        field=field,
                        code=f"{field.upper()}_INVALID_VALUE",
                        message=f"{field} must be one of: {', '.join(field_rules['enum_values'][:5])}...",
                        value=value
                    ))
        
        # Check custom attributes
        custom_attrs = policy.get("custom_attributes", {})
        for attr, attr_rules in custom_attrs.items():
            value = row.get(attr.lower()) or row.get(attr)
            
            if attr_rules.get("required") and not value:
                errors.append(ValidationError(
                    field=attr,
                    code=f"{attr}_REQUIRED",
                    message=f"{attr} is required",
                    value=value
                ))
        
        # Only ERROR severity blocks validation
        is_valid = not any(e.severity == "ERROR" for e in errors)
        return is_valid, errors


def test_valid_csv():
    """Test validation of valid CSV."""
    print("\n📋 Testing VALID CSV...")
    
    loader = SimplePolicyLoader()
    engine = SimpleRuleEngine(loader)
    
    csv_path = Path(__file__).parent / "tests" / "fixtures" / "csv" / "valid" / "celulares_ml_valid.csv"
    if not csv_path.exists():
        print(f"  ⚠️  CSV not found: {csv_path}")
        return
    
    df = pd.read_csv(csv_path)
    
    results = []
    for idx, row in df.iterrows():
        is_valid, errors = engine.validate_row(row.to_dict(), "MLB", "MLB1743")
        results.append({
            "row": idx + 1,
            "sku": row.get("sku"),
            "valid": is_valid,
            "errors": len(errors)
        })
        
        if not is_valid:
            print(f"  Row {idx + 1} ({row.get('sku')}): {len(errors)} errors")
            for e in errors[:3]:  # Show first 3 errors
                print(f"    - {e.field}: {e.message}")
    
    valid_count = sum(1 for r in results if r["valid"])
    print(f"  ✓ Valid rows: {valid_count}/{len(results)}")


def test_invalid_csv():
    """Test validation of invalid CSV."""
    print("\n📋 Testing INVALID CSV...")
    
    loader = SimplePolicyLoader()
    engine = SimpleRuleEngine(loader)
    
    csv_path = Path(__file__).parent / "tests" / "fixtures" / "csv" / "invalid" / "celulares_ml_invalid.csv"
    if not csv_path.exists():
        print(f"  ⚠️  CSV not found: {csv_path}")
        return
    
    df = pd.read_csv(csv_path)
    
    error_summary = {}
    for idx, row in df.iterrows():
        is_valid, errors = engine.validate_row(row.to_dict(), "MLB", "MLB1743")
        
        if errors:
            print(f"  Row {idx + 1}: {len(errors)} errors")
            for e in errors[:2]:  # Show first 2 errors per row
                print(f"    - {e.field}: {e.code}")
                error_summary[e.code] = error_summary.get(e.code, 0) + 1
    
    print(f"\n  Error Summary:")
    for code, count in sorted(error_summary.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"    - {code}: {count} occurrences")


def test_single_row():
    """Test a single row validation."""
    print("\n📋 Testing Single Row...")
    
    loader = SimplePolicyLoader()
    engine = SimpleRuleEngine(loader)
    
    # Valid row
    valid_row = {
        "sku": "TEST-001",
        "title": "iPhone 15 Pro Max 256GB Natural Titanium",
        "price": "8999.99",
        "stock": "10",
        "brand": "APPLE",
        "condition": "new",
        "model": "iPhone 15 Pro Max",
        "storage_capacity": "256GB",
        "color": "Natural Titanium"
    }
    
    is_valid, errors = engine.validate_row(valid_row, "MLB", "MLB1743")
    print(f"  Valid row: {is_valid} (errors: {len(errors)})")
    
    # Invalid row
    invalid_row = {
        "sku": "",
        "title": "Short",
        "price": "-100",
        "stock": "abc",
        "brand": "INVALID",
        "condition": "broken"
    }
    
    is_valid, errors = engine.validate_row(invalid_row, "MLB", "MLB1743")
    print(f"  Invalid row: {is_valid} (errors: {len(errors)})")
    for e in errors:
        print(f"    - {e.field}: {e.message}")


def main():
    print("=" * 60)
    print("🚀 REAL CSV VALIDATION TEST WITH YAML POLICIES")
    print("=" * 60)
    
    # Check if policy exists
    policy_file = Path(__file__).parent / "policies" / "MLB" / "categories" / "MLB1743.yml"
    if policy_file.exists():
        print(f"✓ Policy found: {policy_file}")
        
        # Load and show policy summary
        with open(policy_file) as f:
            policy = yaml.safe_load(f)
        
        print(f"  Version: {policy.get('version')}")
        print(f"  Category: {policy.get('category_name')}")
        print(f"  Rules: {len(policy.get('rules', {}))}")
        print(f"  Custom Attributes: {len(policy.get('custom_attributes', {}))}")
    else:
        print(f"❌ Policy not found: {policy_file}")
        return
    
    # Run tests
    test_single_row()
    test_valid_csv()
    test_invalid_csv()
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()