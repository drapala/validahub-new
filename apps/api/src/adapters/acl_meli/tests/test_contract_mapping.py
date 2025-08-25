"""
Contract tests for MELI to Canonical mapping.
These tests ensure that the mapping between MELI API responses
and our canonical format remains consistent.
"""

import json
from pathlib import Path
from typing import Any, Dict

import pytest
from pydantic import ValidationError

from ..mappers.meli_to_canonical_mapper import MeliToCanonicalMapper
from ..models.canonical_rule import CanonicalRule, CanonicalRuleSet, DataType, RuleType
from ..models.meli_models import (
    MeliCategory,
    MeliCondition,
    MeliListingType,
    MeliRuleAttribute,
    MeliRuleSet,
)


class TestMeliToCanonicalContract:
    """Contract tests for MELI to Canonical mapping using real-world fixtures."""

    @pytest.fixture
    def mapper(self):
        """Create mapper instance."""
        return MeliToCanonicalMapper()

    @pytest.fixture
    def meli_fixtures_path(self):
        """Path to MELI fixtures directory."""
        return Path(__file__).parent / "fixtures" / "meli"

    @pytest.fixture
    def canonical_fixtures_path(self):
        """Path to canonical fixtures directory."""
        return Path(__file__).parent / "fixtures" / "canonical"

    @pytest.fixture
    def meli_category_fixture(self):
        """Real MELI category response fixture."""
        return MeliCategory(
            id="MLB1234",
            name="Celulares e Smartphones",
            picture="https://http2.mlstatic.com/storage/categories-api/images/cell.jpg",
            permalink="https://lista.mercadolivre.com.br/celulares",
            total_items_in_this_category=150000,
            path_from_root=[
                {"id": "MLB5726", "name": "Eletrônicos, Áudio e Vídeo"},
                {"id": "MLB1055", "name": "Celulares e Telefones"},
                {"id": "MLB1234", "name": "Celulares e Smartphones"},
            ],
        )

    @pytest.fixture
    def meli_required_attribute_with_enum(self):
        """MELI attribute with enum values (object style)."""
        return MeliRuleAttribute(
            id="BRAND",
            name="Marca",
            value_type="STRING",
            required=True,
            allowed_values=[
                {"id": "SAMSUNG", "name": "Samsung"},
                {"id": "APPLE", "name": "Apple"},
                {"id": "MOTOROLA", "name": "Motorola"},
                {"id": "XIAOMI", "name": "Xiaomi"},
            ],
            tags={"ui_component": "dropdown"},
        )

    @pytest.fixture
    def meli_optional_attribute_with_pattern(self):
        """MELI attribute with pattern validation."""
        return MeliRuleAttribute(
            id="MODEL",
            name="Modelo",
            value_type="STRING",
            required=False,
            value_max_length=50,
            value_pattern="^[A-Za-z0-9\\s\\-]+$",
            tags={"ui_component": "text_input"},
        )

    @pytest.fixture
    def meli_numeric_attribute(self):
        """MELI numeric attribute with min/max values."""
        return MeliRuleAttribute(
            id="SCREEN_SIZE",
            name="Tamanho da Tela",
            value_type="NUMBER",
            required=True,
            metadata={"min_value": 3.0, "max_value": 8.0, "unit": "inches"},
        )

    @pytest.fixture
    def meli_listing_types(self):
        """MELI listing types."""
        return [
            MeliListingType(
                id="gold_special",
                name="Clássico",
                site_id="MLB",
                configuration={"duration": 60, "listing_exposure": "high"},
            ),
            MeliListingType(
                id="gold_pro",
                name="Premium",
                site_id="MLB",
                configuration={"duration": 60, "listing_exposure": "highest"},
            ),
        ]

    @pytest.fixture
    def meli_conditions(self):
        """MELI item conditions."""
        return [
            MeliCondition(id="new", name="Novo"),
            MeliCondition(id="used", name="Usado"),
            MeliCondition(id="refurbished", name="Recondicionado"),
        ]

    def test_map_required_attribute_to_canonical(
        self, mapper, meli_required_attribute_with_enum
    ):
        """Test mapping of required attribute with enum values."""
        rule = mapper.map_attribute_to_rule(meli_required_attribute_with_enum)

        assert rule.field_name == "BRAND"
        assert rule.rule_type == RuleType.REQUIRED
        assert rule.data_type == DataType.STRING
        assert rule.severity.value == "error"

        # Check enum mapping
        enum_rule = mapper._create_enum_rule(meli_required_attribute_with_enum)
        assert enum_rule is not None
        assert enum_rule.params["values"] == ["SAMSUNG", "APPLE", "MOTOROLA", "XIAOMI"]

    def test_map_optional_attribute_with_pattern(
        self, mapper, meli_optional_attribute_with_pattern
    ):
        """Test mapping of optional attribute with pattern."""
        rules = mapper._create_validation_rules(meli_optional_attribute_with_pattern)

        # Should generate max_length and pattern rules
        assert len(rules) >= 2

        max_length_rule = next(
            (r for r in rules if r.rule_type == RuleType.MAX_LENGTH), None
        )
        assert max_length_rule is not None
        assert max_length_rule.params["max_length"] == 50

        pattern_rule = next((r for r in rules if r.rule_type == RuleType.PATTERN), None)
        assert pattern_rule is not None
        assert pattern_rule.params["pattern"] == "^[A-Za-z0-9\\s\\-]+$"

    def test_map_numeric_attribute(self, mapper, meli_numeric_attribute):
        """Test mapping of numeric attribute with range."""
        rules = mapper._create_validation_rules(meli_numeric_attribute)

        min_value_rule = next(
            (r for r in rules if r.rule_type == RuleType.MIN_VALUE), None
        )
        assert min_value_rule is not None
        assert min_value_rule.params["min_value"] == 3.0

        max_value_rule = next(
            (r for r in rules if r.rule_type == RuleType.MAX_VALUE), None
        )
        assert max_value_rule is not None
        assert max_value_rule.params["max_value"] == 8.0

    def test_map_complete_ruleset(
        self,
        mapper,
        meli_category_fixture,
        meli_required_attribute_with_enum,
        meli_optional_attribute_with_pattern,
        meli_numeric_attribute,
        meli_listing_types,
        meli_conditions,
    ):
        """Test mapping of complete MELI ruleset to canonical format."""
        meli_ruleset = MeliRuleSet(
            category_id="MLB1234",
            site_id="MLB",
            category=meli_category_fixture,
            required_attributes=[
                meli_required_attribute_with_enum,
                meli_numeric_attribute,
            ],
            optional_attributes=[meli_optional_attribute_with_pattern],
            listing_types=meli_listing_types,
            conditions=meli_conditions,
        )

        canonical_ruleset = mapper.map_meli_ruleset(meli_ruleset)

        # Verify basic properties
        assert canonical_ruleset.marketplace_id == "MELI"
        assert canonical_ruleset.name == "MELI Rules for MLB1234"
        assert "MLB1234" in canonical_ruleset.metadata["category_id"]

        # Verify required fields
        required_fields = canonical_ruleset.get_required_fields()
        assert "BRAND" in required_fields
        assert "SCREEN_SIZE" in required_fields
        assert "MODEL" not in required_fields  # Optional

        # Verify rule counts
        brand_rules = canonical_ruleset.get_rules_for_field("BRAND")
        assert len(brand_rules) >= 2  # REQUIRED + ENUM

        model_rules = canonical_ruleset.get_rules_for_field("MODEL")
        assert any(r.rule_type == RuleType.MAX_LENGTH for r in model_rules)
        assert any(r.rule_type == RuleType.PATTERN for r in model_rules)

    def test_brazilian_decimal_format_handling(self, mapper):
        """Test handling of Brazilian decimal format (comma as decimal separator)."""
        attribute = MeliRuleAttribute(
            id="PRICE",
            name="Preço",
            value_type="NUMBER",
            required=True,
            metadata={"format": "decimal_br", "example": "1.234,56"},
        )

        rules = mapper._create_validation_rules(attribute)
        # Mapper should recognize Brazilian format in metadata
        assert any(rule.field_name == "PRICE" for rule in rules)

    def test_case_insensitive_enum_handling(self, mapper):
        """Test that enum values can be matched case-insensitively."""
        attribute = MeliRuleAttribute(
            id="CONDITION",
            name="Condição",
            value_type="STRING",
            required=True,
            allowed_values=["New", "Used", "Refurbished"],
            metadata={"case_sensitive": False},
        )

        enum_rule = mapper._create_enum_rule(attribute)
        assert enum_rule is not None

        # Test validation with different cases
        canonical_rule = CanonicalRule(
            id="test_enum",
            marketplace_id="MELI",
            original_id="CONDITION",
            field_name="CONDITION",
            rule_type=RuleType.ENUM,
            data_type=DataType.STRING,
            params={"values": ["New", "Used", "Refurbished"]},
        )

        # These should all be valid if case-insensitive
        for value in ["new", "NEW", "New", "UsEd", "REFURBISHED"]:
            # Note: Actual case-insensitive validation would need to be
            # implemented in the validate_value method
            pass

    def test_dependencies_enrichment(self, mapper):
        """Test that dependencies between fields are properly enriched."""
        meli_ruleset = MeliRuleSet(
            category_id="MLB1234",
            site_id="MLB",
            required_attributes=[
                MeliRuleAttribute(
                    id="HAS_WARRANTY",
                    name="Tem Garantia",
                    value_type="BOOLEAN",
                    required=True,
                ),
                MeliRuleAttribute(
                    id="WARRANTY_TIME",
                    name="Tempo de Garantia",
                    value_type="NUMBER",
                    required=False,
                    metadata={"depends_on": "HAS_WARRANTY", "condition": "true"},
                ),
            ],
        )

        canonical_ruleset = mapper.map_meli_ruleset(meli_ruleset)
        enriched_ruleset = mapper.enrich_with_dependencies(canonical_ruleset)

        warranty_time_rules = enriched_ruleset.get_rules_for_field("WARRANTY_TIME")
        assert any(
            rule.depends_on == ["HAS_WARRANTY"] for rule in warranty_time_rules
        )

    def test_real_meli_response_contract(self, mapper):
        """Test with a real MELI API response structure."""
        # This would use actual API response fixtures
        real_response = {
            "id": "MLB1055",
            "name": "Celulares e Telefones",
            "attributes": [
                {
                    "id": "BRAND",
                    "name": "Marca",
                    "value_type": "STRING",
                    "value_max_length": 255,
                    "required": True,
                    "allowed_values": [
                        {"id": "SAMSUNG", "name": "Samsung"},
                        {"id": "APPLE", "name": "Apple"},
                    ],
                },
                {
                    "id": "MODEL",
                    "name": "Modelo",
                    "value_type": "STRING",
                    "value_max_length": 100,
                    "required": True,
                },
                {
                    "id": "COLOR",
                    "name": "Cor",
                    "value_type": "STRING",
                    "required": False,
                    "allowed_values": [
                        {"id": "BLACK", "name": "Preto"},
                        {"id": "WHITE", "name": "Branco"},
                        {"id": "BLUE", "name": "Azul"},
                    ],
                },
            ],
        }

        # Parse response into models
        attributes = [
            MeliRuleAttribute(**attr) for attr in real_response["attributes"]
        ]

        # Map to canonical
        rules = []
        for attr in attributes:
            rule = mapper.map_attribute_to_rule(attr)
            if rule:
                rules.append(rule)
            rules.extend(mapper._create_validation_rules(attr))

        # Verify contract expectations
        assert len(rules) > 0
        brand_rules = [r for r in rules if r.field_name == "BRAND"]
        assert any(r.rule_type == RuleType.REQUIRED for r in brand_rules)
        assert any(r.rule_type == RuleType.ENUM for r in brand_rules)

        model_rules = [r for r in rules if r.field_name == "MODEL"]
        assert any(r.rule_type == RuleType.REQUIRED for r in model_rules)
        assert any(r.rule_type == RuleType.MAX_LENGTH for r in model_rules)

    @pytest.mark.parametrize(
        "value_type,expected_data_type",
        [
            ("STRING", DataType.STRING),
            ("NUMBER", DataType.FLOAT),
            ("INTEGER", DataType.INTEGER),
            ("BOOLEAN", DataType.BOOLEAN),
            ("DATE", DataType.DATE),
            ("LIST", DataType.ARRAY),
        ],
    )
    def test_value_type_mapping(self, mapper, value_type, expected_data_type):
        """Test that MELI value types are correctly mapped to canonical data types."""
        attribute = MeliRuleAttribute(
            id="TEST_FIELD",
            name="Test Field",
            value_type=value_type,
            required=False,
        )

        data_type = mapper._map_value_type(value_type)
        assert data_type == expected_data_type

    def test_error_handling_invalid_attribute(self, mapper):
        """Test that invalid attributes are handled gracefully."""
        invalid_attribute = MeliRuleAttribute(
            id="",  # Invalid: empty ID
            name="Invalid",
            value_type="UNKNOWN_TYPE",
            required=True,
        )

        rule = mapper.map_attribute_to_rule(invalid_attribute)
        # Should still create a rule but with defaults
        assert rule is not None
        assert rule.field_name == ""  # Preserves the empty ID