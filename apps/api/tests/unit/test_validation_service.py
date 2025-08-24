"""
Unit tests for ValidationService.
Tests business logic in isolation using mocks.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime


@pytest.mark.unit
class TestValidationService:
    """Test suite for ValidationService."""
    
    @pytest.fixture
    def validation_service(self):
        """Create ValidationService instance with mocked dependencies."""
        with patch('src.services.csv_validation_service.RuleEngine') as mock_engine:
            from src.services.csv_validation_service import CSVValidationService
            service = CSVValidationService()
            service.rule_engine = mock_engine
            return service
    
    def test_validate_row_with_valid_data(self, validation_service):
        """Test validation of a row with all valid data."""
        # Given
        row = {
            "product_id": "ML123456",
            "title": "iPhone 15 Pro Max",
            "price": 7999.99,
            "stock": 10,
            "category": "Celulares"
        }
        validation_service.rule_engine.validate.return_value = {
            "is_valid": True,
            "errors": []
        }
        
        # When
        result = validation_service.validate_row(row, "mercado_livre")
        
        # Then
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0
        validation_service.rule_engine.validate.assert_called_once()
    
    def test_validate_row_with_missing_product_id(self, validation_service):
        """Test validation fails when product_id is missing."""
        # Given
        row = {
            "product_id": "",
            "title": "Product without ID",
            "price": 100.00,
            "stock": 5
        }
        validation_service.rule_engine.validate.return_value = {
            "is_valid": False,
            "errors": [
                {
                    "field": "product_id",
                    "message": "Product ID is required",
                    "severity": "ERROR"
                }
            ]
        }
        
        # When
        result = validation_service.validate_row(row, "mercado_livre")
        
        # Then
        assert result["is_valid"] is False
        assert len(result["errors"]) == 1
        assert result["errors"][0]["field"] == "product_id"
    
    def test_validate_row_with_negative_price(self, validation_service):
        """Test validation fails for negative price."""
        # Given
        row = {
            "product_id": "ML123456",
            "title": "Test Product",
            "price": -50.00,
            "stock": 10
        }
        validation_service.rule_engine.validate.return_value = {
            "is_valid": False,
            "errors": [
                {
                    "field": "price",
                    "message": "Price must be positive",
                    "severity": "ERROR",
                    "value": -50.00
                }
            ]
        }
        
        # When
        result = validation_service.validate_row(row, "mercado_livre")
        
        # Then
        assert result["is_valid"] is False
        assert result["errors"][0]["field"] == "price"
        assert "positive" in result["errors"][0]["message"].lower()
    
    @pytest.mark.parametrize("stock_value,expected_valid", [
        (0, True),      # Zero stock is valid
        (1, True),      # Positive stock is valid
        (-1, False),    # Negative stock is invalid
        ("abc", False), # Non-numeric stock is invalid
        (None, False),  # Null stock is invalid
        (9999, True),   # Large stock is valid
    ])
    def test_validate_stock_values(self, validation_service, stock_value, expected_valid):
        """Test various stock value validations."""
        # Given
        row = {
            "product_id": "ML123456",
            "title": "Test Product",
            "price": 100.00,
            "stock": stock_value
        }
        validation_service.rule_engine.validate.return_value = {
            "is_valid": expected_valid,
            "errors": [] if expected_valid else [{"field": "stock", "message": "Invalid stock"}]
        }
        
        # When
        result = validation_service.validate_row(row, "mercado_livre")
        
        # Then
        assert result["is_valid"] == expected_valid
    
    @pytest.mark.asyncio
    async def test_validate_csv_batch_processing(self, validation_service):
        """Test batch processing of CSV rows."""
        # Given
        rows = [
            {"product_id": f"ML{i:06d}", "price": i * 10.0}
            for i in range(100)
        ]
        validation_service.rule_engine.validate.return_value = {
            "is_valid": True,
            "errors": []
        }
        
        # When
        results = []
        for row in rows:
            result = validation_service.validate_row(row, "mercado_livre")
            results.append(result)
        
        # Then
        assert len(results) == 100
        assert all(r["is_valid"] for r in results)
        assert validation_service.rule_engine.validate.call_count == 100
    
    def test_validate_with_marketplace_specific_rules(self, validation_service):
        """Test that marketplace-specific rules are applied."""
        # Given
        row = {"product_id": "B00123", "title": "Amazon Product"}
        
        # Mock different responses for different marketplaces
        def marketplace_validation(data, marketplace):
            if marketplace == "amazon":
                return {"is_valid": True, "errors": []}
            else:
                return {"is_valid": False, "errors": [{"field": "product_id", "message": "Invalid format for marketplace"}]}
        
        validation_service.rule_engine.validate.side_effect = lambda d, m: marketplace_validation(d, m)
        
        # When
        amazon_result = validation_service.validate_row(row, "amazon")
        ml_result = validation_service.validate_row(row, "mercado_livre")
        
        # Then
        assert amazon_result["is_valid"] is True
        assert ml_result["is_valid"] is False
    
    def test_validation_performance_tracking(self, validation_service, time_machine):
        """Test that validation performance is tracked."""
        # Given
        row = {"product_id": "ML123456", "price": 100.00}
        validation_service.rule_engine.validate.return_value = {
            "is_valid": True,
            "errors": []
        }
        
        # When
        start_time = datetime.now()
        result = validation_service.validate_row(row, "mercado_livre")
        end_time = datetime.now()
        
        # Then
        processing_time = (end_time - start_time).total_seconds()
        assert processing_time < 0.1  # Should be fast (< 100ms)
        assert result["is_valid"] is True
    
    def test_handle_validation_exception(self, validation_service):
        """Test graceful handling of validation exceptions."""
        # Given
        row = {"product_id": "ML123456"}
        validation_service.rule_engine.validate.side_effect = Exception("Rule engine error")
        
        # When
        result = validation_service.validate_row(row, "mercado_livre")
        
        # Then
        assert result["is_valid"] is False
        assert len(result["errors"]) > 0
        assert "error" in result["errors"][0]["message"].lower()
    
    @patch('src.services.csv_validation_service.get_logger')
    def test_validation_logging(self, mock_logger, validation_service):
        """Test that validation events are properly logged."""
        # Given
        logger = Mock()
        mock_logger.return_value = logger
        row = {"product_id": "ML123456"}
        validation_service.rule_engine.validate.return_value = {
            "is_valid": False,
            "errors": [{"field": "price", "message": "Price is required"}]
        }
        
        # When
        result = validation_service.validate_row(row, "mercado_livre")
        
        # Then
        # Should log validation errors
        logger.warning.assert_called()
        assert "validation" in str(logger.warning.call_args).lower()


@pytest.mark.unit
class TestValidationHelpers:
    """Test validation helper functions."""
    
    def test_is_valid_price(self):
        """Test price validation helper."""
        from src.utils.validators import is_valid_price
        
        assert is_valid_price(10.99) is True
        assert is_valid_price(0) is True
        assert is_valid_price(-1) is False
        assert is_valid_price("abc") is False
        assert is_valid_price(None) is False
        assert is_valid_price(999999.99) is True
    
    def test_is_valid_product_id(self):
        """Test product ID validation helper."""
        from src.utils.validators import is_valid_product_id
        
        assert is_valid_product_id("ML123456") is True
        assert is_valid_product_id("") is False
        assert is_valid_product_id(None) is False
        assert is_valid_product_id("A" * 51) is False  # Too long
        assert is_valid_product_id("123") is True
    
    def test_sanitize_string(self):
        """Test string sanitization helper."""
        from src.utils.validators import sanitize_string
        
        assert sanitize_string("  Hello  ") == "Hello"
        assert sanitize_string("Hello\nWorld") == "Hello World"
        assert sanitize_string("Hello\tWorld") == "Hello World"
        assert sanitize_string(None) == ""
        assert sanitize_string(123) == "123"