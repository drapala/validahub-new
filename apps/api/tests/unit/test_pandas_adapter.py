"""
Unit tests for PandasAdapter.
Tests the pandas implementation of TabularDataPort.
"""

import pytest
import pandas as pd
import numpy as np
from io import StringIO

from infrastructure.adapters.pandas_adapter import PandasAdapter


class TestPandasAdapter:
    """Test suite for PandasAdapter."""
    
    @pytest.fixture
    def adapter(self):
        """Create a PandasAdapter instance."""
        return PandasAdapter()
    
    @pytest.fixture
    def sample_csv(self):
        """Sample CSV content for testing."""
        return """name,age,score
Alice,25,90.5
Bob,30,85.0
Charlie,35,92.3"""
    
    @pytest.fixture
    def csv_with_nulls(self):
        """CSV with null and inf values."""
        return """name,value,score
Alice,10.0,inf
Bob,,85.0
Charlie,-inf,"""
    
    def test_parse_csv_valid(self, adapter, sample_csv):
        """Test parsing valid CSV content."""
        result = adapter.parse_csv(sample_csv)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert list(result.columns) == ['name', 'age', 'score']
    
    def test_parse_csv_empty_raises_error(self, adapter):
        """Test that parsing empty CSV raises ValueError."""
        with pytest.raises(ValueError, match="CSV file is empty"):
            adapter.parse_csv("")
    
    def test_parse_csv_invalid_raises_error(self, adapter):
        """Test that parsing invalid CSV raises ValueError."""
        with pytest.raises(ValueError, match="Failed to parse CSV"):
            adapter.parse_csv("not,a,valid\ncsv,file")
    
    def test_clean_data_handles_inf_and_nan(self, adapter, csv_with_nulls):
        """Test that clean_data replaces inf and NaN with None."""
        df = pd.read_csv(StringIO(csv_with_nulls))
        cleaned = adapter.clean_data(df)
        
        # Check that inf values are replaced with None
        assert cleaned.loc[0, 'score'] is None
        assert cleaned.loc[2, 'value'] is None
        
        # Check that NaN values are replaced with None
        assert cleaned.loc[1, 'value'] is None
        assert cleaned.loc[2, 'score'] is None
    
    def test_to_dict_records(self, adapter, sample_csv):
        """Test conversion to dictionary records."""
        df = adapter.parse_csv(sample_csv)
        records = adapter.to_dict_records(df)
        
        assert isinstance(records, list)
        assert len(records) == 3
        assert records[0] == {'name': 'Alice', 'age': 25, 'score': 90.5}
    
    def test_to_dict_records_none_returns_empty(self, adapter):
        """Test that None data returns empty list."""
        assert adapter.to_dict_records(None) == []
    
    def test_to_csv_string(self, adapter, sample_csv):
        """Test conversion to CSV string."""
        df = adapter.parse_csv(sample_csv)
        csv_output = adapter.to_csv_string(df)
        
        assert isinstance(csv_output, str)
        assert "name,age,score" in csv_output
        assert "Alice,25,90.5" in csv_output
    
    def test_to_csv_string_none_returns_empty(self, adapter):
        """Test that None data returns empty string."""
        assert adapter.to_csv_string(None) == ""
    
    def test_is_empty(self, adapter):
        """Test empty check."""
        # Empty DataFrame
        empty_df = pd.DataFrame()
        assert adapter.is_empty(empty_df) is True
        
        # Non-empty DataFrame
        df = pd.DataFrame({'a': [1, 2]})
        assert adapter.is_empty(df) is False
        
        # None
        assert adapter.is_empty(None) is True
    
    def test_row_count(self, adapter, sample_csv):
        """Test row counting."""
        df = adapter.parse_csv(sample_csv)
        assert adapter.row_count(df) == 3
        
        # Empty DataFrame
        assert adapter.row_count(pd.DataFrame()) == 0
        
        # None
        assert adapter.row_count(None) == 0
    
    def test_column_count(self, adapter, sample_csv):
        """Test column counting."""
        df = adapter.parse_csv(sample_csv)
        assert adapter.column_count(df) == 3
        
        # Empty DataFrame
        assert adapter.column_count(pd.DataFrame()) == 0
        
        # None
        assert adapter.column_count(None) == 0
    
    def test_get_columns(self, adapter, sample_csv):
        """Test getting column names."""
        df = adapter.parse_csv(sample_csv)
        columns = adapter.get_columns(df)
        
        assert columns == ['name', 'age', 'score']
        
        # None
        assert adapter.get_columns(None) == []
    
    def test_select_columns(self, adapter, sample_csv):
        """Test column selection."""
        df = adapter.parse_csv(sample_csv)
        selected = adapter.select_columns(df, ['name', 'score'])
        
        assert list(selected.columns) == ['name', 'score']
        assert len(selected) == 3
    
    def test_select_columns_missing_raises_error(self, adapter, sample_csv):
        """Test that selecting non-existent columns raises error."""
        df = adapter.parse_csv(sample_csv)
        
        with pytest.raises(KeyError, match="Columns not found"):
            adapter.select_columns(df, ['name', 'nonexistent'])
    
    def test_filter_rows(self, adapter, sample_csv):
        """Test row filtering."""
        df = adapter.parse_csv(sample_csv)
        filtered = adapter.filter_rows(df, {'name': 'Alice'})
        
        assert len(filtered) == 1
        assert filtered.iloc[0]['name'] == 'Alice'
    
    def test_filter_rows_multiple_conditions(self, adapter, sample_csv):
        """Test filtering with multiple conditions."""
        df = adapter.parse_csv(sample_csv)
        filtered = adapter.filter_rows(df, {'name': 'Bob', 'age': 30})
        
        assert len(filtered) == 1
        assert filtered.iloc[0]['name'] == 'Bob'
    
    def test_filter_rows_no_match(self, adapter, sample_csv):
        """Test filtering with no matches."""
        df = adapter.parse_csv(sample_csv)
        filtered = adapter.filter_rows(df, {'name': 'David'})
        
        assert len(filtered) == 0
    
    def test_adapter_preserves_data_immutability(self, adapter, sample_csv):
        """Test that adapter methods don't modify original data."""
        df = adapter.parse_csv(sample_csv)
        original_copy = df.copy()
        
        # Run various operations
        adapter.clean_data(df)
        adapter.to_dict_records(df)
        adapter.to_csv_string(df)
        adapter.select_columns(df, ['name'])
        adapter.filter_rows(df, {'name': 'Alice'})
        
        # Check original is unchanged
        pd.testing.assert_frame_equal(df, original_copy)