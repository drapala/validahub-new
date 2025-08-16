"""
Unit tests for use cases.
Tests business logic in isolation from infrastructure.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, MagicMock
from io import StringIO

from src.core.use_cases import (
    ValidateCsvUseCase,
    CorrectCsvUseCase,
    ValidateRowUseCase
)
from src.core.use_cases.validate_csv import ValidateCsvInput
from src.core.use_cases.correct_csv import CorrectCsvInput
from src.core.use_cases.validate_row import ValidateRowInput
from src.schemas.validate import (
    Marketplace,
    Category,
    ValidationResult,
    ValidationSummary,
    ValidationItem,
    ValidationStatus
)


class TestValidateCsvUseCase:
    """Test ValidateCsvUseCase business logic."""
    
    @pytest.fixture
    def mock_pipeline(self):
        """Create a mock validation pipeline."""
        pipeline = Mock()
        return pipeline
    
    @pytest.fixture
    def use_case(self, mock_pipeline):
        """Create use case with mocked dependencies."""
        return ValidateCsvUseCase(validation_pipeline=mock_pipeline)
    
    @pytest.fixture
    def sample_csv(self):
        """Sample CSV content for testing."""
        return """title,price,stock
Product 1,10.99,5
Product 2,20.50,0
Product 3,15.00,10"""
    
    @pytest.mark.asyncio
    async def test_execute_successful_validation(self, use_case, mock_pipeline, sample_csv):
        """Test successful CSV validation."""
        # Setup
        input_data = ValidateCsvInput(
            csv_content=sample_csv,
            marketplace=Marketplace.MERCADO_LIVRE,
            category=Category.ELETRONICOS,
            auto_fix=False
        )
        
        mock_result = ValidationResult(
            total_rows=3,
            valid_rows=3,
            error_rows=0,
            validation_items=[],
            summary=ValidationSummary(
                total_errors=0,
                total_warnings=0,
                total_corrections=0,
                error_types={},
                processing_time_seconds=0.1
            ),
            marketplace="MERCADO_LIVRE",
            category="ELETRONICOS",
            auto_fix_applied=False
        )
        
        mock_pipeline.validate.return_value = mock_result
        
        # Execute
        result = await use_case.execute(input_data)
        
        # Assert
        assert result.total_rows == 3
        assert result.valid_rows == 3
        assert result.error_rows == 0
        assert result.job_id is not None
        
        # Verify pipeline was called correctly
        mock_pipeline.validate.assert_called_once()
        call_args = mock_pipeline.validate.call_args
        assert call_args.kwargs['marketplace'] == Marketplace.MERCADO_LIVRE
        assert call_args.kwargs['category'] == Category.ELETRONICOS
        assert call_args.kwargs['auto_fix'] is False
    
    @pytest.mark.asyncio
    async def test_execute_with_auto_fix(self, use_case, mock_pipeline, sample_csv):
        """Test CSV validation with auto-fix enabled."""
        # Setup
        input_data = ValidateCsvInput(
            csv_content=sample_csv,
            marketplace=Marketplace.SHOPEE,
            category=Category.MODA,
            auto_fix=True
        )
        
        # Create a mock corrected DataFrame
        corrected_df = pd.DataFrame({
            'title': ['Product 1', 'Product 2', 'Product 3'],
            'price': [10.99, 20.50, 15.00],
            'stock': [5, 1, 10]  # Stock fixed from 0 to 1
        })
        
        mock_result = ValidationResult(
            total_rows=3,
            valid_rows=3,
            error_rows=0,
            validation_items=[],
            summary=ValidationSummary(
                total_errors=0,
                total_warnings=0,
                total_corrections=1,
                error_types={},
                processing_time_seconds=0.1
            ),
            corrected_data=corrected_df,
            marketplace="SHOPEE",
            category="MODA",
            auto_fix_applied=True
        )
        
        mock_pipeline.validate.return_value = mock_result
        
        # Execute
        result = await use_case.execute(input_data)
        
        # Assert
        assert result.auto_fix_applied is True
        assert result.corrected_data is not None
        assert isinstance(result.corrected_data, list)
        assert len(result.corrected_data) == 3
    
    @pytest.mark.asyncio
    async def test_execute_empty_csv_error(self, use_case, mock_pipeline):
        """Test handling of empty CSV."""
        # Setup
        input_data = ValidateCsvInput(
            csv_content="",
            marketplace=Marketplace.AMAZON,
            category=Category.ELETRONICOS
        )
        
        # Execute and assert
        with pytest.raises(ValueError, match="CSV file is empty or invalid"):
            await use_case.execute(input_data)
    
    @pytest.mark.asyncio
    async def test_execute_invalid_csv_error(self, use_case, mock_pipeline):
        """Test handling of invalid CSV."""
        # Setup
        input_data = ValidateCsvInput(
            csv_content="not,a,valid\ncsv file",
            marketplace=Marketplace.AMAZON,
            category=Category.ELETRONICOS
        )
        
        mock_pipeline.validate.side_effect = Exception("Processing error")
        
        # Execute and assert
        with pytest.raises(Exception, match="Processing error"):
            await use_case.execute(input_data)


class TestCorrectCsvUseCase:
    """Test CorrectCsvUseCase business logic."""
    
    @pytest.fixture
    def mock_pipeline(self):
        """Create a mock validation pipeline."""
        pipeline = Mock()
        return pipeline
    
    @pytest.fixture
    def use_case(self, mock_pipeline):
        """Create use case with mocked dependencies."""
        return CorrectCsvUseCase(validation_pipeline=mock_pipeline)
    
    @pytest.fixture
    def sample_csv(self):
        """Sample CSV content for testing."""
        return """title,price,stock
Product 1,10.99,5
Product 2,20.50,0
Product 3,15.00,10"""
    
    @pytest.mark.asyncio
    async def test_execute_successful_correction(self, use_case, mock_pipeline, sample_csv):
        """Test successful CSV correction."""
        # Setup
        input_data = CorrectCsvInput(
            csv_content=sample_csv,
            marketplace=Marketplace.MERCADO_LIVRE,
            category=Category.ELETRONICOS,
            original_filename="test.csv"
        )
        
        # Create a mock corrected DataFrame
        corrected_df = pd.DataFrame({
            'title': ['Product 1', 'Product 2', 'Product 3'],
            'price': [10.99, 20.50, 15.00],
            'stock': [5, 1, 10]  # Stock fixed from 0 to 1
        })
        
        mock_result = ValidationResult(
            total_rows=3,
            valid_rows=3,
            error_rows=0,
            validation_items=[],
            summary=ValidationSummary(
                total_errors=0,
                total_warnings=0,
                total_corrections=1,
                error_types={},
                processing_time_seconds=0.5
            ),
            corrected_data=corrected_df,
            marketplace="MERCADO_LIVRE",
            category="ELETRONICOS",
            auto_fix_applied=True
        )
        
        mock_pipeline.validate.return_value = mock_result
        
        # Execute
        result = await use_case.execute(input_data)
        
        # Assert
        assert result.original_filename == "test.csv"
        assert result.total_corrections == 1
        assert result.total_errors == 0
        assert result.processing_time == 0.5
        assert result.job_id is not None
        assert "Product 1" in result.corrected_csv
        assert "Product 2" in result.corrected_csv
        
        # Verify pipeline was called with auto_fix=True
        mock_pipeline.validate.assert_called_once()
        call_args = mock_pipeline.validate.call_args
        assert call_args.kwargs['auto_fix'] is True
    
    @pytest.mark.asyncio
    async def test_execute_no_corrections_needed(self, use_case, mock_pipeline, sample_csv):
        """Test when no corrections are needed."""
        # Setup
        input_data = CorrectCsvInput(
            csv_content=sample_csv,
            marketplace=Marketplace.SHOPEE,
            category=Category.MODA
        )
        
        mock_result = ValidationResult(
            total_rows=3,
            valid_rows=3,
            error_rows=0,
            validation_items=[],
            summary=ValidationSummary(
                total_errors=0,
                total_warnings=0,
                total_corrections=0,
                error_types={},
                processing_time_seconds=0.3
            ),
            corrected_data=None,  # No corrections needed
            marketplace="SHOPEE",
            category="MODA",
            auto_fix_applied=True
        )
        
        mock_pipeline.validate.return_value = mock_result
        
        # Execute
        result = await use_case.execute(input_data)
        
        # Assert
        assert result.total_corrections == 0
        assert result.corrected_csv == sample_csv  # Original content returned


class TestValidateRowUseCase:
    """Test ValidateRowUseCase business logic."""
    
    @pytest.fixture
    def mock_pipeline(self):
        """Create a mock validation pipeline."""
        pipeline = Mock()
        return pipeline
    
    @pytest.fixture
    def use_case(self, mock_pipeline):
        """Create use case with mocked dependencies."""
        return ValidateRowUseCase(validation_pipeline=mock_pipeline)
    
    @pytest.fixture
    def sample_row(self):
        """Sample row data for testing."""
        return {
            'title': 'Product 1',
            'price': 10.99,
            'stock': 0
        }
    
    @pytest.mark.asyncio
    async def test_execute_successful_validation(self, use_case, mock_pipeline, sample_row):
        """Test successful row validation."""
        # Setup
        input_data = ValidateRowInput(
            row_data=sample_row,
            marketplace=Marketplace.AMAZON,
            category=Category.ELETRONICOS,
            row_number=5,
            auto_fix=False
        )
        
        mock_items = [
            ValidationItem(
                row_number=5,
                status=ValidationStatus.WARNING,
                errors=[],
                corrections=[]
            )
        ]
        
        mock_pipeline.validate_single_row.return_value = (sample_row, mock_items)
        
        # Execute
        result = await use_case.execute(input_data)
        
        # Assert
        assert result.original_row == sample_row
        assert result.fixed_row is None  # auto_fix was False
        assert result.has_errors is False
        assert result.has_warnings is True
        assert result.auto_fix_applied is False
        
        # Verify pipeline was called correctly
        mock_pipeline.validate_single_row.assert_called_once_with(
            row=sample_row,
            marketplace=Marketplace.AMAZON,
            category=Category.ELETRONICOS,
            row_number=5,
            auto_fix=False
        )
    
    @pytest.mark.asyncio
    async def test_execute_with_auto_fix(self, use_case, mock_pipeline, sample_row):
        """Test row validation with auto-fix."""
        # Setup
        input_data = ValidateRowInput(
            row_data=sample_row,
            marketplace=Marketplace.MERCADO_LIVRE,
            category=Category.MODA,
            row_number=1,
            auto_fix=True
        )
        
        fixed_row = {
            'title': 'Product 1',
            'price': 10.99,
            'stock': 1  # Fixed from 0 to 1
        }
        
        mock_items = [
            ValidationItem(
                row_number=1,
                status=ValidationStatus.ERROR,
                errors=[],
                corrections=[]
            )
        ]
        
        mock_pipeline.validate_single_row.return_value = (fixed_row, mock_items)
        
        # Execute
        result = await use_case.execute(input_data)
        
        # Assert
        assert result.original_row == sample_row
        assert result.fixed_row == fixed_row
        assert result.has_errors is True
        assert result.auto_fix_applied is True