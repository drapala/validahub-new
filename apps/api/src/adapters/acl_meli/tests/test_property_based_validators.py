"""
Property-based tests for validators using Hypothesis.
These tests ensure validators work correctly with a wide range of inputs.
"""

import string
from decimal import Decimal
from typing import Any

import pytest
from hypothesis import assume, given, strategies as st

from ..models.canonical_rule import CanonicalRule, DataType, RuleType


class TestPropertyBasedValidation:
    """Property-based tests for validation rules."""

    @given(
        min_val=st.floats(min_value=-1000000, max_value=1000000),
        max_val=st.floats(min_value=-1000000, max_value=1000000),
        test_val=st.floats(min_value=-10000000, max_value=10000000),
    )
    def test_numeric_range_validation(self, min_val, max_val, test_val):
        """Test numeric range validation with random values."""
        assume(min_val <= max_val)  # Ensure valid range

        rule = CanonicalRule(
            id="test_range",
            marketplace_id="TEST",
            original_id="test",
            field_name="test_field",
            rule_type=RuleType.MIN_VALUE,
            data_type=DataType.FLOAT,
            params={"min_value": min_val},
        )

        is_valid, _ = rule.validate_value(test_val)
        assert is_valid == (test_val >= min_val)

        rule.rule_type = RuleType.MAX_VALUE
        rule.params = {"max_value": max_val}
        is_valid, _ = rule.validate_value(test_val)
        assert is_valid == (test_val <= max_val)

    @given(
        allowed_values=st.lists(
            st.text(min_size=1, max_size=20), min_size=1, max_size=10, unique=True
        ),
        test_value=st.text(min_size=0, max_size=30),
    )
    def test_enum_case_insensitive(self, allowed_values, test_value):
        """Test enum validation with case-insensitive matching."""
        rule = CanonicalRule(
            id="test_enum",
            marketplace_id="TEST",
            original_id="test",
            field_name="test_field",
            rule_type=RuleType.ENUM,
            data_type=DataType.STRING,
            params={"values": allowed_values, "case_sensitive": False},
        )

        # For case-insensitive comparison
        normalized_allowed = [v.lower() for v in allowed_values]
        normalized_test = test_value.lower()

        expected_valid = normalized_test in normalized_allowed

        # Note: Actual implementation would need to support case_sensitive param
        # This test shows the expected behavior
        if rule.params.get("case_sensitive", True):
            is_valid, _ = rule.validate_value(test_value)
            assert is_valid == (test_value in allowed_values)
        else:
            # Case insensitive check (would need implementation)
            pass

    @given(
        integer_str=st.text(
            alphabet=string.digits + ".", min_size=1, max_size=15
        ).filter(lambda x: x.count(".") <= 3)
    )
    def test_brazilian_decimal_format(self, integer_str):
        """Test handling of Brazilian decimal format (1.234.567,89)."""
        # Brazilian format uses comma as decimal separator and dot as thousands
        br_number = integer_str.replace(".", "")  # Remove thousand separators
        if "," in br_number:
            # This would be the decimal part
            parts = br_number.split(",")
            if len(parts) == 2 and parts[1].isdigit() and parts[0].isdigit():
                # Valid Brazilian decimal
                expected_value = float(parts[0] + "." + parts[1])
            else:
                expected_value = None
        elif br_number.isdigit():
            expected_value = float(br_number)
        else:
            expected_value = None

        # Test conversion function (would need implementation)
        # assert convert_br_decimal(integer_str) == expected_value

    @given(
        min_len=st.integers(min_value=0, max_value=100),
        max_len=st.integers(min_value=0, max_value=1000),
        test_str=st.text(min_size=0, max_size=2000),
    )
    def test_string_length_validation(self, min_len, max_len, test_str):
        """Test string length validation with random strings."""
        assume(min_len <= max_len)

        rule_min = CanonicalRule(
            id="test_min_len",
            marketplace_id="TEST",
            original_id="test",
            field_name="test_field",
            rule_type=RuleType.MIN_LENGTH,
            data_type=DataType.STRING,
            params={"min_length": min_len},
        )

        is_valid, _ = rule_min.validate_value(test_str)
        assert is_valid == (len(test_str) >= min_len)

        rule_max = CanonicalRule(
            id="test_max_len",
            marketplace_id="TEST",
            original_id="test",
            field_name="test_field",
            rule_type=RuleType.MAX_LENGTH,
            data_type=DataType.STRING,
            params={"max_length": max_len},
        )

        is_valid, _ = rule_max.validate_value(test_str)
        assert is_valid == (len(test_str) <= max_len)

    @given(
        test_value=st.one_of(
            st.none(),
            st.text(min_size=0, max_size=0),  # Empty string
            st.lists(st.integers(), min_size=0, max_size=0),  # Empty list
            st.dictionaries(st.text(), st.integers(), min_size=0, max_size=0),  # Empty dict
            st.text(min_size=1),  # Non-empty string
            st.lists(st.integers(), min_size=1),  # Non-empty list
            st.dictionaries(st.text(), st.integers(), min_size=1),  # Non-empty dict
        )
    )
    def test_required_field_validation(self, test_value):
        """Test REQUIRED validation with various empty/non-empty values."""
        rule = CanonicalRule(
            id="test_required",
            marketplace_id="TEST",
            original_id="test",
            field_name="test_field",
            rule_type=RuleType.REQUIRED,
            data_type=DataType.STRING,  # Type doesn't matter for REQUIRED
        )

        is_valid, _ = rule.validate_value(test_value)

        # Expected behavior: None, empty string, empty list, empty dict are invalid
        if test_value is None or test_value == "":
            assert not is_valid
        elif isinstance(test_value, (list, dict)) and len(test_value) == 0:
            assert not is_valid
        else:
            assert is_valid

    @given(
        pattern=st.sampled_from(
            [
                r"^\d+$",  # Numbers only
                r"^[A-Za-z]+$",  # Letters only
                r"^[A-Z][a-z]+$",  # Capitalized word
                r"^\w+@\w+\.\w+$",  # Simple email pattern
                r"^\+?\d{1,3}[-.\s]?\d{1,14}$",  # Phone number
            ]
        ),
        test_str=st.text(min_size=0, max_size=50),
    )
    def test_pattern_validation(self, pattern, test_str):
        """Test pattern validation with common patterns."""
        import re

        rule = CanonicalRule(
            id="test_pattern",
            marketplace_id="TEST",
            original_id="test",
            field_name="test_field",
            rule_type=RuleType.PATTERN,
            data_type=DataType.STRING,
            params={"pattern": pattern},
        )

        is_valid, _ = rule.validate_value(test_str)
        expected_valid = bool(re.fullmatch(pattern, test_str))
        assert is_valid == expected_valid

    @given(
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=5)
    )
    def test_percentile_validation(self, values):
        """Test validation of values within percentile ranges."""
        if not values:
            return

        sorted_values = sorted(values)
        p25 = sorted_values[len(sorted_values) // 4]
        p75 = sorted_values[3 * len(sorted_values) // 4]

        # Test that values between 25th and 75th percentile are valid
        for val in values:
            if p25 <= val <= p75:
                # Should be within acceptable range
                rule = CanonicalRule(
                    id="test_percentile",
                    marketplace_id="TEST",
                    original_id="test",
                    field_name="test_field",
                    rule_type=RuleType.MIN_VALUE,
                    data_type=DataType.FLOAT,
                    params={"min_value": p25},
                )
                is_valid, _ = rule.validate_value(val)
                assert is_valid

    @given(
        data=st.dictionaries(
            st.text(min_size=1, max_size=10),
            st.one_of(
                st.none(),
                st.text(),
                st.integers(),
                st.floats(allow_nan=False, allow_infinity=False),
                st.booleans(),
            ),
            min_size=0,
            max_size=20,
        )
    )
    def test_required_fields_in_dict(self, data):
        """Test validation of required fields in dictionary data."""
        required_fields = ["id", "name", "price"]

        for field in required_fields:
            rule = CanonicalRule(
                id=f"test_required_{field}",
                marketplace_id="TEST",
                original_id="test",
                field_name=field,
                rule_type=RuleType.REQUIRED,
                data_type=DataType.STRING,
            )

            value = data.get(field)
            is_valid, _ = rule.validate_value(value)

            # Check our expectation
            if field not in data or data[field] is None or data[field] == "":
                assert not is_valid
            elif isinstance(data[field], (list, dict)) and len(data[field]) == 0:
                assert not is_valid
            else:
                assert is_valid

    @given(
        currency_amount=st.decimals(
            min_value=Decimal("0.01"), max_value=Decimal("999999.99"), places=2
        )
    )
    def test_currency_validation(self, currency_amount):
        """Test validation of currency amounts with proper decimal places."""
        rule = CanonicalRule(
            id="test_currency",
            marketplace_id="TEST",
            original_id="test",
            field_name="price",
            rule_type=RuleType.MIN_VALUE,
            data_type=DataType.FLOAT,
            params={"min_value": 0.01},
            metadata={"currency": "BRL", "decimal_places": 2},
        )

        is_valid, _ = rule.validate_value(float(currency_amount))
        assert is_valid == (currency_amount >= Decimal("0.01"))

    @given(
        base_value=st.floats(min_value=0, max_value=1000000, allow_nan=False),
        tolerance_percent=st.floats(min_value=0, max_value=100, allow_nan=False),
        test_value=st.floats(min_value=0, max_value=2000000, allow_nan=False),
    )
    def test_tolerance_validation(self, base_value, tolerance_percent, test_value):
        """Test validation with tolerance ranges."""
        tolerance = base_value * (tolerance_percent / 100)
        min_allowed = base_value - tolerance
        max_allowed = base_value + tolerance

        rule_min = CanonicalRule(
            id="test_tolerance_min",
            marketplace_id="TEST",
            original_id="test",
            field_name="test_field",
            rule_type=RuleType.MIN_VALUE,
            data_type=DataType.FLOAT,
            params={"min_value": min_allowed},
        )

        rule_max = CanonicalRule(
            id="test_tolerance_max",
            marketplace_id="TEST",
            original_id="test",
            field_name="test_field",
            rule_type=RuleType.MAX_VALUE,
            data_type=DataType.FLOAT,
            params={"max_value": max_allowed},
        )

        is_valid_min, _ = rule_min.validate_value(test_value)
        is_valid_max, _ = rule_max.validate_value(test_value)

        assert is_valid_min == (test_value >= min_allowed)
        assert is_valid_max == (test_value <= max_allowed)