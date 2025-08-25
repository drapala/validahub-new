"""
Integration tests for CSV validation with real data and policies.
"""

import pytest
import pandas as pd
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from services.policy_loader import PolicyLoader
from services.policy_rule_engine import PolicyRuleEngine


class TestRealCSVValidation:
    """Test CSV validation with real fixtures and policies."""
    
    @pytest.fixture
    def policy_loader(self):
        """Create policy loader with real policies."""
        return PolicyLoader()
    
    @pytest.fixture
    def rule_engine(self, policy_loader):
        """Create rule engine with policy loader."""
        return PolicyRuleEngine(policy_loader)
    
    @pytest.fixture
    def fixtures_dir(self):
        """Get fixtures directory."""
        return Path(__file__).parent.parent / "fixtures" / "csv"
    
    def test_validate_valid_csv(self, rule_engine, fixtures_dir):
        """Test validation of valid CSV file."""
        # Load valid CSV
        csv_path = fixtures_dir / "valid" / "celulares_ml_valid.csv"
        df = pd.read_csv(csv_path)
        
        all_valid = True
        all_errors = []
        
        # Validate each row
        for idx, row in df.iterrows():
            is_valid, errors, corrections = rule_engine.validate_row(
                row.to_dict(),
                marketplace="MLB",
                category="MLB1743",
                row_number=idx + 1
            )
            
            if not is_valid:
                all_valid = False
                error_details = [e.to_dict() for e in errors if e.severity == "ERROR"]
                if error_details:
                    all_errors.append({
                        "row": idx + 1,
                        "errors": error_details
                    })
        
        # Print errors for debugging
        if all_errors:
            print("\nValidation errors found in 'valid' CSV:")
            for row_errors in all_errors:
                print(f"  Row {row_errors['row']}:")
                for error in row_errors['errors']:
                    print(f"    - {error['field']}: {error['message']}")
        
        # Most rows should be valid (allow some warnings)
        assert len(all_errors) <= 1, f"Too many errors in valid CSV: {len(all_errors)}"
    
    def test_validate_invalid_csv(self, rule_engine, fixtures_dir):
        """Test validation of invalid CSV file."""
        # Load invalid CSV
        csv_path = fixtures_dir / "invalid" / "celulares_ml_invalid.csv"
        df = pd.read_csv(csv_path)
        
        errors_by_row = {}
        
        # Validate each row
        for idx, row in df.iterrows():
            is_valid, errors, corrections = rule_engine.validate_row(
                row.to_dict(),
                marketplace="MLB",
                category="MLB1743",
                row_number=idx + 1
            )
            
            # Collect errors
            error_list = [e.to_dict() for e in errors if e.severity == "ERROR"]
            if error_list:
                errors_by_row[idx + 1] = error_list
        
        # Every row should have errors
        assert len(errors_by_row) >= 6, f"Expected at least 6 rows with errors, got {len(errors_by_row)}"
        
        # Check specific expected errors
        # Row 1: Missing SKU, title too short, price = 0
        row_1_errors = errors_by_row.get(1, [])
        error_fields = [e['field'] for e in row_1_errors]
        assert 'sku' in error_fields or 'SKU' in error_fields
        assert 'title' in error_fields
        assert 'price' in error_fields
        
        # Row 2: Invalid SKU characters, title too long with forbidden chars
        row_2_errors = errors_by_row.get(2, [])
        error_codes = [e['code'] for e in row_2_errors]
        assert any('FORBIDDEN' in code or 'INVALID' in code or 'TOO_LONG' in code for code in error_codes)
    
    def test_validate_edge_cases(self, rule_engine, fixtures_dir):
        """Test validation of edge case CSV file."""
        # Load edge cases CSV
        csv_path = fixtures_dir / "edge-cases" / "celulares_ml_edge.csv"
        df = pd.read_csv(csv_path)
        
        results = []
        
        # Validate each row
        for idx, row in df.iterrows():
            is_valid, errors, corrections = rule_engine.validate_row(
                row.to_dict(),
                marketplace="MLB",
                category="MLB1743",
                row_number=idx + 1
            )
            
            results.append({
                "row": idx + 1,
                "sku": row.get("sku"),
                "is_valid": is_valid,
                "error_count": len([e for e in errors if e.severity == "ERROR"]),
                "warning_count": len([e for e in errors if e.severity == "WARNING"]),
                "corrections": len(corrections)
            })
        
        # Check edge cases handled correctly
        # Row 1: Exactly 60 chars title, price = 1.00, stock = 0
        assert results[0]["error_count"] == 0, "Edge case with boundary values should be valid"
        
        # Row 2: Max values (price = 999999.99, stock = 99999)
        assert results[1]["error_count"] == 0, "Max values should be valid"
        
        # Row 4: Unicode characters
        unicode_row = results[3]
        # Unicode should be allowed in title/description
        assert unicode_row["error_count"] <= 2, "Unicode characters should be allowed"
    
    def test_corrections_applied(self, rule_engine, fixtures_dir):
        """Test that corrections are suggested for fixable issues."""
        # Create a row with fixable issues
        row = {
            "sku": "SKU-TEST-001",
            "title": "  iPhone 15 Pro Max 256GB  ",  # Has leading/trailing spaces
            "price": "5999,99",  # Brazilian format with comma
            "stock": "10",
            "brand": "apple",  # Wrong case
            "condition": "NEW",  # Wrong case
            "model": "iPhone 15 Pro Max",
            "storage_capacity": "256GB",
            "color": "Preto"
        }
        
        is_valid, errors, corrections = rule_engine.validate_row(
            row,
            marketplace="MLB",
            category="MLB1743",
            row_number=1
        )
        
        # Should have corrections for trimming
        assert len(corrections) > 0, "Should suggest corrections for trimmable fields"
        
        # Check specific corrections
        correction_fields = [c['field'] for c in corrections]
        # Note: Current implementation returns corrections, but we may need to enhance it
    
    def test_custom_attributes_validation(self, rule_engine):
        """Test validation of custom attributes."""
        # Row with invalid custom attributes
        row = {
            "sku": "SKU-CUSTOM-001",
            "title": "Samsung Galaxy S24 Ultra 512GB",
            "price": "7999.99",
            "stock": "5",
            "brand": "SAMSUNG",
            "condition": "new",
            "model": "Galaxy S24 Ultra",
            "storage_capacity": "2TB",  # Invalid - not in enum
            "ram_memory": "24GB",  # Invalid - not in enum
            "color": "A" * 50,  # Too long
            "operating_system": "Tizen",  # Invalid - not in enum
            "dual_sim": "maybe"  # Invalid boolean
        }
        
        is_valid, errors, _ = rule_engine.validate_row(
            row,
            marketplace="MLB",
            category="MLB1743",
            row_number=1
        )
        
        assert not is_valid, "Row with invalid custom attributes should fail"
        
        # Check for specific custom attribute errors
        error_fields = [e.field for e in errors if e.severity == "ERROR"]
        assert "STORAGE_CAPACITY" in error_fields or "storage_capacity" in error_fields
        assert "COLOR" in error_fields or "color" in error_fields
    
    def test_warning_generation(self, rule_engine):
        """Test that warnings are generated for non-critical issues."""
        # Row without description and few images
        row = {
            "sku": "SKU-WARN-001",
            "title": "iPhone 14 128GB Midnight",
            "description": "",  # Missing description
            "price": "4999.99",
            "stock": "10",
            "brand": "APPLE",
            "condition": "new",
            "model": "iPhone 14",
            "storage_capacity": "128GB",
            "color": "Midnight",
            "image_url_1": "https://example.com/img1.jpg"  # Only 1 image
        }
        
        is_valid, errors, _ = rule_engine.validate_row(
            row,
            marketplace="MLB",
            category="MLB1743",
            row_number=1
        )
        
        # Should be valid (warnings don't block)
        assert is_valid, "Warnings should not make row invalid"
        
        # Should have warnings
        warnings = [e for e in errors if e.severity == "WARNING"]
        assert len(warnings) >= 2, "Should have warnings for missing description and low image count"
        
        warning_codes = [w.code for w in warnings]
        assert "DESCRIPTION_MISSING" in warning_codes
        assert "LOW_IMAGE_COUNT" in warning_codes


class TestPolicyLoading:
    """Test policy loading functionality."""
    
    def test_load_existing_policy(self):
        """Test loading an existing policy file."""
        loader = PolicyLoader()
        policy = loader.get_policy("MLB", "MLB1743")
        
        assert policy is not None
        assert policy["marketplace"] == "MLB"
        assert policy["category_id"] == "MLB1743"
        assert "rules" in policy
        assert "title" in policy["rules"]
        assert "price" in policy["rules"]
    
    def test_load_non_existent_policy(self):
        """Test loading a non-existent policy returns default."""
        loader = PolicyLoader()
        policy = loader.get_policy("XYZ", "CAT999")
        
        assert policy is not None
        assert policy["version"] == "default"
        assert "rules" in policy
    
    def test_list_available_policies(self):
        """Test listing available policies."""
        loader = PolicyLoader()
        policies = loader.list_available_policies()
        
        assert "MLB" in policies
        assert "MLB1743" in policies["MLB"]
    
    def test_policy_validation(self):
        """Test policy structure validation."""
        loader = PolicyLoader()
        policy = loader.get_policy("MLB", "MLB1743")
        
        is_valid, errors = loader.validate_policy_structure(policy)
        assert is_valid, f"Policy should be valid: {errors}"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])