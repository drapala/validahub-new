"""
Unit tests for MELI to Canonical mapper.
"""

import pytest
import json
from pathlib import Path

from ..models.meli_models import MeliRuleAttribute, MeliCategory
from ..models.canonical_rule import RuleType, DataType, RuleSeverity
from ..mappers.meli_to_canonical_mapper import MeliToCanonicalMapper


class TestMeliToCanonicalMapper:
    """Test cases for the MELI to Canonical mapper."""
    
    @pytest.fixture
    def mapper(self):
        """Create mapper instance."""
        return MeliToCanonicalMapper(marketplace_id="MELI")
    
    @pytest.fixture
    def sample_attribute_required(self):
        """Create a sample required attribute."""
        return MeliRuleAttribute(
            id="BRAND",
            name="Marca",
            value_type="STRING",
            value_max_length=60,
            required=True,
            allowed_values=["Samsung", "Apple", "Xiaomi"]
        )
    
    @pytest.fixture
    def sample_attribute_optional(self):
        """Create a sample optional attribute."""
        return MeliRuleAttribute(
            id="COLOR",
            name="Cor",
            value_type="STRING",
            value_max_length=50,
            required=False,
            allowed_values=["Preto", "Branco", "Azul"]
        )
    
    @pytest.fixture
    def sample_attribute_with_pattern(self):
        """Create a sample attribute with pattern validation."""
        return MeliRuleAttribute(
            id="GTIN",
            name="Código universal de produto",
            value_type="STRING",
            value_pattern="^\\d{8,14}$",
            required=False
        )
    
    @pytest.fixture
    def sample_category(self):
        """Load sample category from fixture."""
        fixture_path = Path(__file__).parent / "fixtures" / "meli_category_response.json"
        with open(fixture_path, "r") as f:
            data = json.load(f)
        
        # Convert attributes to MeliRuleAttribute objects
        data["attributes"] = [
            MeliRuleAttribute(**attr) for attr in data["attributes"]
        ]
        
        return MeliCategory(**data)
    
    def test_map_required_attribute(self, mapper, sample_attribute_required):
        """Test mapping a required attribute."""
        rules = mapper.map_attribute_to_rules(sample_attribute_required)
        
        # Should generate at least 2 rules: required and enum
        assert len(rules) >= 2
        
        # Check required rule
        required_rule = next(
            (r for r in rules if r.rule_type == RuleType.REQUIRED),
            None
        )
        assert required_rule is not None
        assert required_rule.field_name == "BRAND"
        assert required_rule.severity == RuleSeverity.ERROR
        assert required_rule.data_type == DataType.STRING
        
        # Check enum rule
        enum_rule = next(
            (r for r in rules if r.rule_type == RuleType.ENUM),
            None
        )
        assert enum_rule is not None
        assert enum_rule.params["values"] == ["Samsung", "Apple", "Xiaomi"]
    
    def test_map_optional_attribute(self, mapper, sample_attribute_optional):
        """Test mapping an optional attribute."""
        rules = mapper.map_attribute_to_rules(sample_attribute_optional)
        
        # Should not have required rule
        required_rule = next(
            (r for r in rules if r.rule_type == RuleType.REQUIRED),
            None
        )
        assert required_rule is None
        
        # Should have max_length rule
        max_length_rule = next(
            (r for r in rules if r.rule_type == RuleType.MAX_LENGTH),
            None
        )
        assert max_length_rule is not None
        assert max_length_rule.params["max_length"] == 50
    
    def test_map_attribute_with_pattern(self, mapper, sample_attribute_with_pattern):
        """Test mapping an attribute with pattern validation."""
        rules = mapper.map_attribute_to_rules(sample_attribute_with_pattern)
        
        # Should have pattern rule
        pattern_rule = next(
            (r for r in rules if r.rule_type == RuleType.PATTERN),
            None
        )
        assert pattern_rule is not None
        assert pattern_rule.params["pattern"] == "^\\d{8,14}$"
        assert pattern_rule.field_name == "GTIN"
    
    def test_map_category_to_ruleset(self, mapper, sample_category):
        """Test mapping a complete category to ruleset."""
        ruleset = mapper.map_category_to_ruleset(sample_category)
        
        assert ruleset.marketplace_id == "MELI"
        assert ruleset.name == "Celulares e Telefones Rules"
        assert len(ruleset.rules) > 0
        
        # Check that required fields are mapped
        required_fields = ruleset.get_required_fields()
        assert "BRAND" in required_fields
        assert "MODEL" in required_fields
        
        # Check metadata
        assert ruleset.metadata["category_id"] == "MLB1051"
        assert ruleset.metadata["category_name"] == "Celulares e Telefones"
    
    def test_type_mapping(self, mapper):
        """Test data type mapping."""
        # String type
        attr = MeliRuleAttribute(
            id="TEST",
            name="Test",
            value_type="STRING",
            required=False
        )
        rules = mapper.map_attribute_to_rules(attr)
        assert any(r.data_type == DataType.STRING for r in rules)
        
        # Number type
        attr.value_type = "NUMBER"
        rules = mapper.map_attribute_to_rules(attr)
        assert any(r.data_type == DataType.FLOAT for r in rules)
        
        # Boolean type
        attr.value_type = "BOOLEAN"
        rules = mapper.map_attribute_to_rules(attr)
        assert any(r.data_type == DataType.BOOLEAN for r in rules)
    
    def test_length_validation_rules(self, mapper):
        """Test generation of length validation rules."""
        attr = MeliRuleAttribute(
            id="DESCRIPTION",
            name="Descrição",
            value_type="STRING",
            value_min_length=10,
            value_max_length=500,
            required=False
        )
        
        rules = mapper.map_attribute_to_rules(attr)
        
        # Should have both min and max length rules
        min_length_rule = next(
            (r for r in rules if r.rule_type == RuleType.MIN_LENGTH),
            None
        )
        assert min_length_rule is not None
        assert min_length_rule.params["min_length"] == 10
        
        max_length_rule = next(
            (r for r in rules if r.rule_type == RuleType.MAX_LENGTH),
            None
        )
        assert max_length_rule is not None
        assert max_length_rule.params["max_length"] == 500
    
    def test_rule_metadata(self, mapper, sample_attribute_required):
        """Test that rules contain proper metadata."""
        rules = mapper.map_attribute_to_rules(sample_attribute_required)
        
        for rule in rules:
            assert rule.marketplace_id == "MELI"
            assert rule.original_id == "BRAND"
            assert "meli" in rule.tags
            assert rule.metadata["original_name"] == "Marca"
            assert rule.metadata["meli_id"] == "BRAND"
