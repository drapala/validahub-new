"""
Tests for the validation registry system.
"""

import pytest
from datetime import datetime, date
from core.validation.registry import ValidationRegistry, ValidatorSpec
from core.validation.validators_builtin import register_builtin_validators
from adapters.acl_meli.models.canonical_rule import DataType


@pytest.fixture
def registry():
    """Create a fresh registry for each test."""
    reg = ValidationRegistry()
    register_builtin_validators(DataType)
    return reg


@pytest.fixture
def clean_registry():
    """Create an empty registry without built-in validators."""
    return ValidationRegistry()


class TestValidationRegistry:
    """Test the core registry functionality."""
    
    def test_register_and_validate(self, clean_registry):
        """Test basic registration and validation."""
        # Register a simple validator
        clean_registry.register(
            "test_key",
            lambda v: v == "valid",
            meta=ValidatorSpec(name="test", description="Test validator")
        )
        
        assert clean_registry.has("test_key")
        assert clean_registry.validate("test_key", "valid")
        assert not clean_registry.validate("test_key", "invalid")
    
    def test_default_validator(self, clean_registry):
        """Test default validator behavior."""
        # Default is permissive
        assert clean_registry.validate("unknown_key", "anything")
        
        # Change default to restrictive
        clean_registry.set_default(lambda v: False)
        assert not clean_registry.validate("unknown_key", "anything")
    
    def test_override_registration(self, clean_registry):
        """Test that last registration wins."""
        clean_registry.register("key", lambda v: v == "first")
        assert clean_registry.validate("key", "first")
        assert not clean_registry.validate("key", "second")
        
        # Override with new validator
        clean_registry.register("key", lambda v: v == "second")
        assert not clean_registry.validate("key", "first")
        assert clean_registry.validate("key", "second")
    
    def test_metadata(self, clean_registry):
        """Test validator metadata."""
        spec = ValidatorSpec(name="test", description="A test validator")
        clean_registry.register("key", lambda v: True, meta=spec)
        
        retrieved = clean_registry.describe("key")
        assert retrieved == spec
        assert retrieved.name == "test"
        assert retrieved.description == "A test validator"
    
    def test_list_validators(self, clean_registry):
        """Test listing all validators."""
        spec1 = ValidatorSpec(name="val1")
        spec2 = ValidatorSpec(name="val2")
        
        clean_registry.register("key1", lambda v: True, meta=spec1)
        clean_registry.register("key2", lambda v: True, meta=spec2)
        
        validators = clean_registry.list_validators()
        assert len(validators) == 2
        assert validators["key1"] == spec1
        assert validators["key2"] == spec2
    
    def test_clear(self, clean_registry):
        """Test clearing the registry."""
        clean_registry.register("key", lambda v: True)
        assert clean_registry.has("key")
        
        clean_registry.clear()
        assert not clean_registry.has("key")


class TestBuiltinValidators:
    """Test the built-in type validators."""
    
    def test_string_validation(self, registry):
        """Test string type validation."""
        assert registry.validate(DataType.STRING, "hello")
        assert registry.validate(DataType.STRING, "")
        assert not registry.validate(DataType.STRING, 123)
        assert not registry.validate(DataType.STRING, None)
    
    def test_integer_without_bool(self, registry):
        """Test that integers don't accept booleans."""
        assert registry.validate(DataType.INTEGER, 42)
        assert registry.validate(DataType.INTEGER, 0)
        assert registry.validate(DataType.INTEGER, -1)
        assert not registry.validate(DataType.INTEGER, True)
        assert not registry.validate(DataType.INTEGER, False)
        assert not registry.validate(DataType.INTEGER, 3.14)
        assert not registry.validate(DataType.INTEGER, "42")
    
    def test_float_accepts_int_not_bool(self, registry):
        """Test that float accepts int but not bool."""
        assert registry.validate(DataType.FLOAT, 3.14)
        assert registry.validate(DataType.FLOAT, 0.0)
        assert registry.validate(DataType.FLOAT, 42)  # int is ok
        assert registry.validate(DataType.FLOAT, -1)
        assert not registry.validate(DataType.FLOAT, True)
        assert not registry.validate(DataType.FLOAT, False)
        assert not registry.validate(DataType.FLOAT, "3.14")
    
    def test_boolean_validation(self, registry):
        """Test boolean type validation."""
        assert registry.validate(DataType.BOOLEAN, True)
        assert registry.validate(DataType.BOOLEAN, False)
        assert not registry.validate(DataType.BOOLEAN, 1)
        assert not registry.validate(DataType.BOOLEAN, 0)
        assert not registry.validate(DataType.BOOLEAN, "true")
    
    def test_date_datetime_validation(self, registry):
        """Test date and datetime validation."""
        now = datetime.utcnow()
        today = date.today()
        
        # DATE accepts str, datetime, and date
        assert registry.validate(DataType.DATE, "2025-08-25")
        assert registry.validate(DataType.DATE, now)
        assert registry.validate(DataType.DATE, today)
        assert not registry.validate(DataType.DATE, 123)
        
        # DATETIME accepts str and datetime (not date alone)
        assert registry.validate(DataType.DATETIME, "2025-08-25T10:30:00")
        assert registry.validate(DataType.DATETIME, now)
        assert not registry.validate(DataType.DATETIME, 123)
    
    def test_array_validation(self, registry):
        """Test array type validation."""
        assert registry.validate(DataType.ARRAY, [1, 2, 3])
        assert registry.validate(DataType.ARRAY, [])
        assert registry.validate(DataType.ARRAY, (1, 2, 3))
        assert not registry.validate(DataType.ARRAY, "not an array")
        assert not registry.validate(DataType.ARRAY, {"key": "value"})
    
    def test_object_validation(self, registry):
        """Test object (dict) type validation."""
        assert registry.validate(DataType.OBJECT, {"key": "value"})
        assert registry.validate(DataType.OBJECT, {})
        assert not registry.validate(DataType.OBJECT, [1, 2, 3])
        assert not registry.validate(DataType.OBJECT, "not an object")
    
    def test_unknown_type_is_permissive(self, registry):
        """Test that unknown types are permissive by default."""
        class UnknownType:
            pass
        
        # Should return True for unknown types
        assert registry.validate(UnknownType, "anything")
        assert registry.validate(UnknownType, 123)
        assert registry.validate(UnknownType, None)


class TestExtensibility:
    """Test the extensibility of the registry."""
    
    def test_custom_validator(self, registry):
        """Test adding custom validators."""
        # Add a custom email validator
        import re
        email_pattern = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
        
        class CustomType:
            EMAIL = "email"
        
        registry.register(
            CustomType.EMAIL,
            lambda v: isinstance(v, str) and email_pattern.match(v) is not None,
            meta=ValidatorSpec(name="email", description="Validates email addresses")
        )
        
        assert registry.validate(CustomType.EMAIL, "user@example.com")
        assert not registry.validate(CustomType.EMAIL, "invalid-email")
        assert not registry.validate(CustomType.EMAIL, 123)
    
    def test_marketplace_specific_types(self, registry):
        """Test adding marketplace-specific types."""
        # Simulate adding a MELI-specific type
        class MeliTypes:
            MELI_ID = "meli_id"
        
        # MELI IDs are strings starting with "MLB"
        registry.register(
            MeliTypes.MELI_ID,
            lambda v: isinstance(v, str) and v.startswith("MLB"),
            meta=ValidatorSpec(name="meli_id", description="MELI product ID")
        )
        
        assert registry.validate(MeliTypes.MELI_ID, "MLB123456")
        assert not registry.validate(MeliTypes.MELI_ID, "MLA123456")  # Argentina
        assert not registry.validate(MeliTypes.MELI_ID, 123456)