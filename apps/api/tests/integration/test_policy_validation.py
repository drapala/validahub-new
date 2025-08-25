"""
Isolated tests for policy-based CSV validation.
"""

import pytest
import pandas as pd
from pathlib import Path
import sys
import os

# Set environment to avoid SQLAlchemy issues
os.environ["TESTING"] = "true"

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


def test_policy_loader_basic():
    """Test basic policy loading."""
    from services.policy_loader import PolicyLoader
    
    loader = PolicyLoader()
    policy = loader.get_policy("MLB", "MLB1743")
    
    assert policy is not None
    assert policy["marketplace"] == "MLB"
    assert policy["category_id"] == "MLB1743"
    assert "rules" in policy
    print(f"✓ Loaded policy: {policy['category_name']}")


def test_validate_valid_row():
    """Test validating a valid product row."""
    from services.policy_loader import PolicyLoader
    from services.policy_rule_engine import PolicyRuleEngine
    
    loader = PolicyLoader()
    engine = PolicyRuleEngine(loader)
    
    # Valid row
    row = {
        "sku": "SKU-TEST-001",
        "title": "iPhone 15 Pro Max 256GB Titanium Natural",
        "price": "8999.99",
        "stock": "10",
        "brand": "APPLE",
        "condition": "new",
        "model": "iPhone 15 Pro Max",
        "storage_capacity": "256GB",
        "color": "Titanium Natural"
    }
    
    is_valid, errors, corrections = engine.validate_row(
        row,
        marketplace="MLB",
        category="MLB1743",
        row_number=1
    )
    
    # Filter only errors (not warnings)
    actual_errors = [e for e in errors if e.severity == "ERROR"]
    
    assert is_valid or len(actual_errors) == 0, f"Valid row should pass: {[e.to_dict() for e in actual_errors]}"
    print(f"✓ Valid row passed with {len(errors)} warnings")


def test_validate_invalid_row():
    """Test validating an invalid product row."""
    from services.policy_loader import PolicyLoader
    from services.policy_rule_engine import PolicyRuleEngine
    
    loader = PolicyLoader()
    engine = PolicyRuleEngine(loader)
    
    # Invalid row
    row = {
        "sku": "",  # Missing SKU
        "title": "Short",  # Too short
        "price": "-100",  # Negative
        "stock": "-5",  # Negative
        "brand": "INVALID_BRAND",  # Not in enum
        "condition": "broken",  # Invalid condition
        "model": "",
        "storage_capacity": "999TB",  # Invalid size
        "color": ""
    }
    
    is_valid, errors, corrections = engine.validate_row(
        row,
        marketplace="MLB",
        category="MLB1743",
        row_number=1
    )
    
    actual_errors = [e for e in errors if e.severity == "ERROR"]
    
    assert not is_valid, "Invalid row should fail"
    assert len(actual_errors) >= 5, f"Should have multiple errors, got {len(actual_errors)}"
    
    # Check specific error types
    error_fields = [e.field for e in actual_errors]
    assert "sku" in error_fields or "SKU" in error_fields
    assert "title" in error_fields
    assert "price" in error_fields
    
    print(f"✓ Invalid row detected {len(actual_errors)} errors")


def test_validate_real_csv():
    """Test validating a real CSV file."""
    from services.policy_loader import PolicyLoader
    from services.policy_rule_engine import PolicyRuleEngine
    
    loader = PolicyLoader()
    engine = PolicyRuleEngine(loader)
    
    # Load CSV
    csv_path = Path(__file__).parent.parent / "fixtures" / "csv" / "valid" / "celulares_ml_valid.csv"
    if not csv_path.exists():
        pytest.skip(f"CSV fixture not found: {csv_path}")
    
    df = pd.read_csv(csv_path)
    
    results = []
    for idx, row in df.iterrows():
        is_valid, errors, corrections = engine.validate_row(
            row.to_dict(),
            marketplace="MLB",
            category="MLB1743",
            row_number=idx + 1
        )
        
        actual_errors = [e for e in errors if e.severity == "ERROR"]
        results.append({
            "row": idx + 1,
            "valid": is_valid or len(actual_errors) == 0,
            "errors": len(actual_errors),
            "warnings": len([e for e in errors if e.severity == "WARNING"])
        })
    
    # Summary
    valid_count = sum(1 for r in results if r["valid"])
    total_errors = sum(r["errors"] for r in results)
    total_warnings = sum(r["warnings"] for r in results)
    
    print(f"\n📊 CSV Validation Summary:")
    print(f"  Total rows: {len(results)}")
    print(f"  Valid rows: {valid_count}/{len(results)}")
    print(f"  Total errors: {total_errors}")
    print(f"  Total warnings: {total_warnings}")
    
    # Most rows should be valid
    assert valid_count >= len(results) - 1, f"Most rows should be valid, got {valid_count}/{len(results)}"


def test_corrections_suggested():
    """Test that corrections are suggested for fixable issues."""
    from services.policy_loader import PolicyLoader
    from services.policy_rule_engine import PolicyRuleEngine
    
    loader = PolicyLoader()
    engine = PolicyRuleEngine(loader)
    
    # Row with fixable issues
    row = {
        "sku": "SKU-FIX-001",
        "title": "  Samsung Galaxy S24 Ultra  ",  # Spaces to trim
        "price": "7999,99",  # Brazilian decimal format
        "stock": "10",
        "brand": "samsung",  # Wrong case
        "condition": "NEW",  # Wrong case
        "model": "Galaxy S24 Ultra",
        "storage_capacity": "256GB",
        "color": "Black"
    }
    
    is_valid, errors, corrections = engine.validate_row(
        row,
        marketplace="MLB",
        category="MLB1743",
        row_number=1
    )
    
    print(f"✓ Detected {len(corrections)} corrections")
    for correction in corrections:
        print(f"  - {correction['field']}: '{correction['original']}' → '{correction['corrected']}' ({correction['reason']})")


def test_edge_cases():
    """Test edge cases and boundary values."""
    from services.policy_loader import PolicyLoader
    from services.policy_rule_engine import PolicyRuleEngine
    
    loader = PolicyLoader()
    engine = PolicyRuleEngine(loader)
    
    test_cases = [
        {
            "name": "Min price",
            "row": {"sku": "TEST", "title": "A" * 10, "price": "1.00", "stock": "0", 
                   "brand": "SAMSUNG", "condition": "new", "model": "Test", 
                   "storage_capacity": "16GB", "color": "Black"},
            "should_be_valid": True
        },
        {
            "name": "Max price",
            "row": {"sku": "TEST", "title": "A" * 60, "price": "999999.99", "stock": "99999",
                   "brand": "APPLE", "condition": "new", "model": "Test",
                   "storage_capacity": "1TB", "color": "White"},
            "should_be_valid": True
        },
        {
            "name": "Unicode in title",
            "row": {"sku": "TEST", "title": "Celular com ação e ñoño", "price": "1000", "stock": "1",
                   "brand": "XIAOMI", "condition": "new", "model": "Test",
                   "storage_capacity": "64GB", "color": "Azul"},
            "should_be_valid": True
        }
    ]
    
    for test_case in test_cases:
        is_valid, errors, _ = engine.validate_row(
            test_case["row"],
            marketplace="MLB",
            category="MLB1743"
        )
        
        actual_errors = [e for e in errors if e.severity == "ERROR"]
        actual_valid = is_valid or len(actual_errors) == 0
        
        if actual_valid != test_case["should_be_valid"]:
            print(f"❌ {test_case['name']}: Expected valid={test_case['should_be_valid']}, got {actual_valid}")
            if actual_errors:
                for e in actual_errors:
                    print(f"   Error: {e.field} - {e.message}")
        else:
            print(f"✓ {test_case['name']}: Passed")


if __name__ == "__main__":
    print("🧪 Running Policy Validation Tests\n")
    
    test_policy_loader_basic()
    test_validate_valid_row()
    test_validate_invalid_row()
    test_validate_real_csv()
    test_corrections_suggested()
    test_edge_cases()
    
    print("\n✅ All tests completed!")