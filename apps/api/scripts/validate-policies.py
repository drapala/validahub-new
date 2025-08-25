#!/usr/bin/env python3
"""
Validate all policy files against the JSON Schema.
Run this in CI/CD to ensure policy files are valid.
"""

import json
import yaml
import sys
from pathlib import Path
from datetime import datetime
from jsonschema import validate, ValidationError, Draft7Validator
from typing import Dict, List, Tuple


def load_schema() -> Dict:
    """Load the policy JSON Schema."""
    schema_path = Path(__file__).parent.parent / "schemas" / "policy-schema.json"
    with open(schema_path) as f:
        return json.load(f)


def find_policy_files() -> List[Path]:
    """Find all YAML policy files."""
    policies_dir = Path(__file__).parent.parent / "policies"
    return list(policies_dir.rglob("*.yml")) + list(policies_dir.rglob("*.yaml"))


def validate_policy_file(file_path: Path, schema: Dict) -> Tuple[bool, str]:
    """
    Validate a single policy file.
    Returns (is_valid, error_message).
    """
    try:
        # Load YAML (keep dates as strings)
        with open(file_path) as f:
            content = f.read()
            # Convert datetime back to ISO string for JSON schema validation
            policy = yaml.safe_load(content)
            
            # Convert datetime objects to ISO strings
            if isinstance(policy.get("effective_date"), datetime):
                policy["effective_date"] = policy["effective_date"].isoformat()
            if isinstance(policy.get("deprecated_after"), datetime):
                policy["deprecated_after"] = policy["deprecated_after"].isoformat()
            if "source" in policy and isinstance(policy["source"].get("last_fetched"), datetime):
                policy["source"]["last_fetched"] = policy["source"]["last_fetched"].isoformat()
        
        # Validate against schema
        validate(instance=policy, schema=schema)
        
        # Additional business logic validations
        rules = policy.get("rules", {})
        
        # Check min <= max for all numeric rules
        for field, rule in rules.items():
            if isinstance(rule, dict):
                if "min_length" in rule and "max_length" in rule:
                    if rule["min_length"] > rule["max_length"]:
                        return False, f"{field}: min_length > max_length"
                
                if "min_value" in rule and "max_value" in rule:
                    if rule["min_value"] > rule["max_value"]:
                        return False, f"{field}: min_value > max_value"
                
                if "min_count" in rule and "max_count" in rule:
                    if rule["min_count"] > rule["max_count"]:
                        return False, f"{field}: min_count > max_count"
        
        # Check that required fields have proper constraints
        for field, rule in rules.items():
            if isinstance(rule, dict) and rule.get("required"):
                if field in ["title", "price", "stock", "brand"]:
                    if not any(k in rule for k in ["min_length", "min_value", "enum_values"]):
                        return False, f"{field}: required field needs constraints"
        
        return True, "Valid"
        
    except yaml.YAMLError as e:
        return False, f"YAML parse error: {e}"
    except ValidationError as e:
        return False, f"Schema validation error: {e.message}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def validate_cross_references(policies: List[Path]) -> List[str]:
    """Check for cross-reference issues between policies."""
    issues = []
    
    # Load all policies
    loaded_policies = {}
    for path in policies:
        with open(path) as f:
            loaded_policies[path] = yaml.safe_load(f)
    
    # Check for version conflicts
    marketplaces = {}
    for path, policy in loaded_policies.items():
        mp = policy.get("marketplace")
        cat = policy.get("category_id")
        version = policy.get("version")
        
        key = (mp, cat)
        if key in marketplaces:
            other_path, other_version = marketplaces[key]
            if version != other_version:
                issues.append(
                    f"Version conflict for {mp}/{cat}: "
                    f"{path} has {version}, {other_path} has {other_version}"
                )
        else:
            marketplaces[key] = (path, version)
    
    return issues


def main():
    """Main validation routine."""
    print("🔍 Validating policy files...")
    
    # Load schema
    try:
        schema = load_schema()
        validator = Draft7Validator(schema)
        print(f"✓ Loaded schema from schemas/policy-schema.json")
    except Exception as e:
        print(f"✗ Failed to load schema: {e}")
        sys.exit(1)
    
    # Find policy files
    policy_files = find_policy_files()
    if not policy_files:
        print("⚠️  No policy files found")
        sys.exit(0)
    
    print(f"📁 Found {len(policy_files)} policy files")
    
    # Validate each file
    errors = []
    for file_path in policy_files:
        is_valid, message = validate_policy_file(file_path, schema)
        
        rel_path = file_path.relative_to(Path(__file__).parent.parent)
        if is_valid:
            print(f"  ✓ {rel_path}")
        else:
            print(f"  ✗ {rel_path}: {message}")
            errors.append((rel_path, message))
    
    # Check cross-references
    cross_issues = validate_cross_references(policy_files)
    if cross_issues:
        print("\n⚠️  Cross-reference issues:")
        for issue in cross_issues:
            print(f"  - {issue}")
            errors.append(("cross-reference", issue))
    
    # Summary
    print(f"\n{'='*50}")
    if errors:
        print(f"❌ Validation failed: {len(errors)} error(s)")
        for path, error in errors[:10]:  # Show first 10 errors
            print(f"  - {path}: {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")
        sys.exit(1)
    else:
        print(f"✅ All {len(policy_files)} policy files are valid!")
        sys.exit(0)


if __name__ == "__main__":
    main()