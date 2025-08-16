"""
Unit tests for refactored validation pipeline.
Tests dependency injection and decoupling from RuleEngineService.
"""

import pytest
import pandas as pd
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock
from typing import List, Dict, Any

from src.core.interfaces.validation import IValidator, IDataAdapter
from src.core.pipeline.validation_pipeline_v2 import (
    ValidationPipelineV2,
    PandasDataAdapter
)
from src.infrastructure.validators.rule_engine_validator import (
    RuleEngineValidator,
    MultiStrategyValidator
)
from src.schemas.validate import (
    ValidationItem,
    ValidationStatus,
    ErrorDetail,
    CorrectionDetail,
    Marketplace,
    Category
)


class TestValidationPipelineV2:
    """Test the refactored validation pipeline."""
    
    @pytest.fixture
    def mock_validator(self):
        """Create a mock validator."""
        validator = AsyncMock(spec=IValidator)
        validator.validate_row.return_value = []
        validator.validate_and_fix_row.return_value = ({}, [])
        return validator
    
    @pytest.fixture
    def sample_df(self):
        """Create sample DataFrame for testing."""
        return pd.DataFrame({
            'title': ['Product 1', 'Product 2'],
            'price': [10.99, 20.50],
            'stock': [5, 0]
        })
    
    @pytest.fixture
    def pipeline(self, mock_validator):
        """Create pipeline with mocked validator."""
        return ValidationPipelineV2(
            validator=mock_validator,
            parallel_processing=False
        )
    
    @pytest.mark.asyncio
    async def test_pipeline_uses_injected_validator(self, pipeline, mock_validator, sample_df):
        """Test that pipeline uses the injected validator."""
        # Act
        result = await pipeline.validate(
            df=sample_df,
            marketplace=Marketplace.MERCADO_LIVRE,
            category=Category.ELETRONICOS,
            auto_fix=False
        )
        
        # Assert - validator was called for each row
        assert mock_validator.validate_row.call_count == 2
        assert result.total_rows == 2
    
    @pytest.mark.asyncio
    async def test_pipeline_no_direct_rule_engine_dependency(self, pipeline):
        """Test that pipeline has no direct RuleEngineService dependency."""
        # Assert - no rule_engine_service attribute
        assert not hasattr(pipeline, 'rule_engine_service')
        
        # Assert - only has validator interface
        assert hasattr(pipeline, 'validator')
        assert isinstance(pipeline.validator, IValidator)
    
    @pytest.mark.asyncio
    async def test_pipeline_with_auto_fix(self, pipeline, mock_validator, sample_df):
        """Test pipeline with auto-fix enabled."""
        # Setup
        mock_validator.validate_and_fix_row.return_value = (
            {'title': 'Product 1', 'price': 10.99, 'stock': 1},
            []
        )
        
        # Act
        result = await pipeline.validate(
            df=sample_df,
            marketplace=Marketplace.SHOPEE,
            category=Category.MODA,
            auto_fix=True
        )
        
        # Assert
        assert mock_validator.validate_and_fix_row.called
        assert result.auto_fix_applied is True
        assert result.corrected_data is not None
    
    @pytest.mark.asyncio
    async def test_pipeline_parallel_processing(self, mock_validator, sample_df):
        """Test pipeline with parallel processing enabled."""
        # Setup
        pipeline = ValidationPipelineV2(
            validator=mock_validator,
            parallel_processing=True,
            batch_size=1
        )
        
        # Act
        result = await pipeline.validate(
            df=sample_df,
            marketplace=Marketplace.AMAZON,
            category=Category.ELETRONICOS,
            auto_fix=False
        )
        
        # Assert - all rows processed
        assert result.total_rows == 2
        assert mock_validator.validate_row.call_count == 2
    
    @pytest.mark.asyncio
    async def test_validate_single_row(self, pipeline, mock_validator):
        """Test single row validation."""
        # Setup
        row = {'title': 'Product', 'price': 15.00}
        mock_validator.validate_row.return_value = [
            ValidationItem(
                row_number=1,
                status=ValidationStatus.WARNING,
                errors=[],
                corrections=[]
            )
        ]
        
        # Act
        fixed_row, items = await pipeline.validate_single_row(
            row=row,
            marketplace=Marketplace.MERCADO_LIVRE,
            row_number=5,
            auto_fix=False
        )
        
        # Assert
        assert fixed_row == row  # No fix applied
        assert len(items) == 1
        assert items[0].status == ValidationStatus.WARNING


class TestRuleEngineValidator:
    """Test the RuleEngineValidator adapter."""
    
    @pytest.fixture
    def mock_rule_engine(self):
        """Create mock rule engine service."""
        engine = Mock()
        engine.validate_row.return_value = []
        engine.validate_and_fix_row.return_value = ({}, [])
        return engine
    
    @pytest.fixture
    def validator(self, mock_rule_engine):
        """Create validator with mocked engine."""
        return RuleEngineValidator(mock_rule_engine)
    
    @pytest.mark.asyncio
    async def test_validator_adapts_rule_engine(self, validator, mock_rule_engine):
        """Test that validator correctly adapts rule engine."""
        # Act
        items = await validator.validate_row(
            row={'price': 10},
            marketplace='mercado_livre',
            row_number=1
        )
        
        # Assert
        mock_rule_engine.validate_row.assert_called_once_with(
            {'price': 10},
            'mercado_livre',
            1
        )
    
    @pytest.mark.asyncio
    async def test_validator_handles_sync_engine(self, mock_rule_engine):
        """Test validator handles synchronous rule engine."""
        # Setup - make validate_row synchronous
        mock_rule_engine.validate_row = Mock(return_value=[])
        validator = RuleEngineValidator(mock_rule_engine)
        
        # Act
        items = await validator.validate_row(
            row={'price': 10},
            marketplace='shopee',
            row_number=2
        )
        
        # Assert - should still work
        assert items == []
        mock_rule_engine.validate_row.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_validate_and_fix_preserves_original(self, validator, mock_rule_engine):
        """Test that validate_and_fix doesn't modify original row."""
        # Setup
        original_row = {'price': 10, 'title': 'Product'}
        mock_rule_engine.validate_and_fix_row.return_value = (
            {'price': 15, 'title': 'Product'},
            []
        )
        
        # Act
        fixed_row, items = await validator.validate_and_fix_row(
            row=original_row,
            marketplace='amazon',
            row_number=1
        )
        
        # Assert
        assert original_row == {'price': 10, 'title': 'Product'}  # Unchanged
        assert fixed_row == {'price': 15, 'title': 'Product'}


class TestMultiStrategyValidator:
    """Test the multi-strategy validator."""
    
    @pytest.fixture
    def validator1(self):
        """First mock validator."""
        v = AsyncMock(spec=IValidator)
        v.validate_row.return_value = [
            ValidationItem(
                row_number=1,
                status=ValidationStatus.ERROR,
                errors=[ErrorDetail(
                    field='price',
                    message='Price too low',
                    code='PRICE_MIN',
                    severity='ERROR'
                )],
                corrections=[]
            )
        ]
        return v
    
    @pytest.fixture
    def validator2(self):
        """Second mock validator."""
        v = AsyncMock(spec=IValidator)
        v.validate_row.return_value = [
            ValidationItem(
                row_number=1,
                status=ValidationStatus.WARNING,
                errors=[],
                corrections=[]
            )
        ]
        return v
    
    @pytest.fixture
    def multi_validator(self, validator1, validator2):
        """Create multi-strategy validator."""
        return MultiStrategyValidator([validator1, validator2])
    
    @pytest.mark.asyncio
    async def test_multi_validator_combines_results(self, multi_validator, validator1, validator2):
        """Test that multi-validator combines results from all validators."""
        # Act
        items = await multi_validator.validate_row(
            row={'price': 5},
            marketplace='mercado_livre',
            row_number=1
        )
        
        # Assert
        assert len(items) == 2  # Results from both validators
        assert any(item.status == ValidationStatus.ERROR for item in items)
        assert any(item.status == ValidationStatus.WARNING for item in items)
        
        # Both validators called
        validator1.validate_row.assert_called_once()
        validator2.validate_row.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_multi_validator_deduplicates(self, validator1):
        """Test that multi-validator deduplicates identical items."""
        # Setup - two validators returning same item
        multi_validator = MultiStrategyValidator([validator1, validator1])
        
        # Act
        items = await multi_validator.validate_row(
            row={'price': 5},
            marketplace='shopee',
            row_number=1
        )
        
        # Assert - deduplicated
        assert len(items) == 1  # Only one unique item


class TestPandasDataAdapter:
    """Test the pandas data adapter."""
    
    @pytest.fixture
    def adapter(self):
        """Create data adapter."""
        return PandasDataAdapter()
    
    def test_dataframe_to_rows(self, adapter):
        """Test DataFrame to rows conversion."""
        # Setup
        df = pd.DataFrame({
            'a': [1, 2],
            'b': [3, 4]
        })
        
        # Act
        rows = adapter.dataframe_to_rows(df)
        
        # Assert
        assert rows == [
            {'a': 1, 'b': 3},
            {'a': 2, 'b': 4}
        ]
    
    def test_rows_to_dataframe(self, adapter):
        """Test rows to DataFrame conversion."""
        # Setup
        rows = [
            {'a': 1, 'b': 3},
            {'a': 2, 'b': 4}
        ]
        
        # Act
        df = adapter.rows_to_dataframe(rows)
        
        # Assert
        assert len(df) == 2
        assert list(df.columns) == ['a', 'b']
    
    def test_normalize_row_handles_nan(self, adapter):
        """Test that normalize handles NaN values."""
        # Setup
        import numpy as np
        row = {
            'a': 1,
            'b': np.nan,
            'c': None,
            'd': 'text'
        }
        
        # Act
        normalized = adapter.normalize_row(row)
        
        # Assert
        assert normalized['a'] == 1
        assert normalized['b'] is None  # NaN converted to None
        assert normalized['c'] is None
        assert normalized['d'] == 'text'