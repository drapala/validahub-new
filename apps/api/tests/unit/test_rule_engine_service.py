"""
Unit tests for RuleEngineService.
"""

import pytest
from pathlib import Path
import sys
import tempfile
import yaml

# Add libs to path
libs_path = Path(__file__).parent.parent.parent.parent.parent / "libs"
sys.path.insert(0, str(libs_path))

from src.services.rule_engine_service import RuleEngineService, RuleEngineConfig
from src.schemas.validate import ValidationStatus, Severity
from src.core.enums import MarketplaceType


@pytest.fixture
def temp_ruleset_dir():
    """Create a temporary directory with test rulesets."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create a test ruleset
        test_ruleset = {
            "version": "1.0",
            "name": "Test Rules",
            "rules": [
                {
                    "id": "test_required",
                    "name": "Test Required Field",
                    "check": {
                        "type": "required",
                        "field": "test_field"
                    },
                    "fix": {
                        "type": "set_default",
                        "field": "test_field",
                        "value": "default_value"
                    },
                    "meta": {
                        "severity": "ERROR"
                    }
                },
                {
                    "id": "price_positive",
                    "name": "Price must be positive",
                    "when": "price",
                    "check": {
                        "type": "numeric_min",
                        "field": "price",
                        "value": 0.01
                    },
                    "meta": {
                        "severity": "ERROR"
                    }
                }
            ]
        }
        
        # Write test ruleset
        ruleset_file = tmpdir_path / "test.yaml"
        with open(ruleset_file, 'w') as f:
            yaml.dump(test_ruleset, f)
        
        # Write default ruleset
        default_file = tmpdir_path / "default.yaml"
        with open(default_file, 'w') as f:
            yaml.dump(test_ruleset, f)
        
        yield tmpdir_path


@pytest.fixture
def rule_engine_service(temp_ruleset_dir):
    """Create RuleEngineService with test configuration."""
    config = RuleEngineConfig(
        rulesets_path=temp_ruleset_dir,
        cache_enabled=False  # Disable cache for testing
    )
    return RuleEngineService(config)


class TestRuleEngineService:
    
    def test_init_service(self, rule_engine_service):
        """Test service initialization."""
        assert rule_engine_service is not None
        assert rule_engine_service.config is not None
        assert rule_engine_service.config.cache_enabled is False
    
    def test_get_engine_for_marketplace(self, rule_engine_service):
        """Test getting engine for a marketplace."""
        engine = rule_engine_service.get_engine_for_marketplace("test")
        assert engine is not None
        assert hasattr(engine, 'execute')
    
    def test_validate_row_missing_required(self, rule_engine_service):
        """Test validation of row with missing required field."""
        row = {"other_field": "value"}
        items = rule_engine_service.validate_row(row, "test", 1)
        
        # Should have error for missing required field
        assert len(items) > 0
        error_item = items[0]
        assert error_item.status == ValidationStatus.ERROR
        assert len(error_item.errors) > 0
        assert error_item.errors[0].code == "test_required"
    
    def test_validate_and_fix_row(self, rule_engine_service):
        """Test validation and fixing of row."""
        row = {"other_field": "value"}  # Missing test_field
        fixed_row, items = rule_engine_service.validate_and_fix_row(
            row, "test", 1, auto_fix=True
        )
        
        # Should have fixed the missing field
        assert "test_field" in fixed_row
        assert fixed_row["test_field"] == "default_value"
        
        # Should have warning/info about the fix
        assert len(items) > 0
        fixed_item = [i for i in items if i.status == ValidationStatus.WARNING]
        if fixed_item:
            assert len(fixed_item[0].corrections) > 0
    
    def test_validate_row_with_numeric_check(self, rule_engine_service):
        """Test numeric validation."""
        row = {"price": -10}
        items = rule_engine_service.validate_row(row, "test", 1)
        
        # Should have error for negative price
        error_items = [i for i in items if i.status == ValidationStatus.ERROR]
        assert len(error_items) > 0
        
        price_error = [e for e in error_items if "price" in str(e.errors[0].code).lower()]
        assert len(price_error) > 0
    
    def test_cache_functionality(self, temp_ruleset_dir):
        """Test that caching works when enabled."""
        config = RuleEngineConfig(
            rulesets_path=temp_ruleset_dir,
            cache_enabled=True
        )
        service = RuleEngineService(config)
        
        # Get engine twice
        engine1 = service.get_engine_for_marketplace("test")
        engine2 = service.get_engine_for_marketplace("test")
        
        # Should be the same cached instance
        assert engine1 is engine2
        
        # Clear cache
        service.clear_cache()
        
        # Get engine again
        engine3 = service.get_engine_for_marketplace("test")
        
        # Should be a new instance
        assert engine3 is not engine1
    
    def test_fallback_to_default_ruleset(self, rule_engine_service):
        """Test fallback to default ruleset when marketplace-specific not found."""
        # Request non-existent marketplace
        engine = rule_engine_service.get_engine_for_marketplace("non_existent")
        
        # Should still get an engine (using default ruleset)
        assert engine is not None
        
        # Validate a row
        row = {"test": "value"}
        items = rule_engine_service.validate_row(row, "non_existent", 1)
        
        # Should still perform validation
        assert isinstance(items, list)
    
    def test_reload_marketplace_rules(self, rule_engine_service):
        """Test reloading rules for a marketplace."""
        # Get engine initially
        engine1 = rule_engine_service.get_engine_for_marketplace("test")
        
        # Reload rules
        rule_engine_service.reload_marketplace_rules("test")
        
        # Get engine again (with cache disabled, should be new)
        engine2 = rule_engine_service.get_engine_for_marketplace("test")
        
        # Both should work
        assert engine1 is not None
        assert engine2 is not None
    
    def test_convert_result_to_validation_item(self, rule_engine_service):
        """Test conversion of RuleResult to ValidationItem."""
        from rule_engine import RuleResult
        
        # Test FAIL result
        result = RuleResult(
            rule_id="test_rule",
            status="FAIL",
            message="Test failed",
            metadata={"field": "test_field", "severity": "ERROR"}
        )
        
        item = rule_engine_service._convert_result_to_validation_item(
            result, 1, {"test_field": "value"}
        )
        
        assert item is not None
        assert item.status == ValidationStatus.ERROR
        assert len(item.errors) > 0
        assert item.errors[0].code == "test_rule"
        
        # Test FIXED result
        result_fixed = RuleResult(
            rule_id="test_rule",
            status="FIXED",
            message="Fixed",
            metadata={"field": "test_field", "fix_type": "auto_fix", "fixed_value": "new_value"}
        )
        
        item_fixed = rule_engine_service._convert_result_to_validation_item(
            result_fixed, 1, {"test_field": "old_value"}
        )
        
        assert item_fixed is not None
        assert item_fixed.status == ValidationStatus.WARNING
        assert len(item_fixed.corrections) > 0
        assert item_fixed.corrections[0].corrected_value == "new_value"
    
    def test_map_severity(self, rule_engine_service):
        """Test severity mapping."""
        from rule_engine import RuleResult
        
        # Test with meta severity
        result = RuleResult(
            rule_id="test",
            status="FAIL",
            message="",
            metadata={"severity": "CRITICAL"}
        )
        severity = rule_engine_service._map_severity(result)
        assert severity == Severity.ERROR
        
        # Test without meta
        result_no_meta = RuleResult(
            rule_id="test",
            status="ERROR",
            message="",
            metadata={}
        )
        severity_no_meta = rule_engine_service._map_severity(result_no_meta)
        assert severity_no_meta == Severity.ERROR