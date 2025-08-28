"""
Pandas implementation of TabularDataPort.

This adapter encapsulates all pandas-specific logic,
keeping the core domain free from infrastructure dependencies.
"""

import pandas as pd
import numpy as np
from typing import Any, List, Dict, Optional, Union
from io import StringIO

from src.core.ports.tabular_data_port import TabularDataPort


class PandasAdapter(TabularDataPort):
    """
    Concrete implementation of TabularDataPort using pandas.
    
    This adapter handles all pandas-specific operations,
    translating between the port interface and pandas DataFrames.
    """
    
    def parse_csv(self, csv_content: Union[str, StringIO]) -> pd.DataFrame:
        """
        Parse CSV content into pandas DataFrame.
        
        Args:
            csv_content: CSV content as string or file-like object
            
        Returns:
            Pandas DataFrame
            
        Raises:
            ValueError: If CSV parsing fails
        """
        try:
            if isinstance(csv_content, str):
                if not csv_content.strip():
                    raise ValueError("CSV file is empty")
                csv_content = StringIO(csv_content)
            
            df = pd.read_csv(csv_content)
            
            if df.empty:
                raise ValueError("CSV file is empty")
                
            return df
            
        except pd.errors.EmptyDataError:
            raise ValueError("CSV file is empty")
        except Exception as e:
            raise ValueError(f"Failed to parse CSV: {str(e)}")
    
    def clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Clean DataFrame by handling NaN and inf values.
        
        Args:
            data: DataFrame to clean
            
        Returns:
            Cleaned DataFrame (copy, not modified in place)
        """
        if data is None:
            return None
            
        # Create a copy to avoid modifying original
        cleaned = data.copy()
        
        # Replace inf values with None
        cleaned = cleaned.replace([np.inf, -np.inf], None)
        
        # Replace NaN values with None (for JSON serialization)
        cleaned = cleaned.where(pd.notnull(cleaned), None)
        
        return cleaned
    
    def to_dict_records(self, data: Optional[pd.DataFrame]) -> List[Dict[str, Any]]:
        """
        Convert DataFrame to list of dictionaries.
        
        Args:
            data: DataFrame to convert
            
        Returns:
            List of dictionaries representing rows
        """
        if data is None:
            return []
        
        # Clean data before conversion
        cleaned = self.clean_data(data)
        return cleaned.to_dict('records')
    
    def to_csv_string(self, data: Optional[pd.DataFrame]) -> str:
        """
        Convert DataFrame to CSV string.
        
        Args:
            data: DataFrame to convert
            
        Returns:
            CSV formatted string
        """
        if data is None:
            return ""
        
        # Clean data before conversion
        cleaned = self.clean_data(data)
        return cleaned.to_csv(index=False)
    
    def is_empty(self, data: Optional[pd.DataFrame]) -> bool:
        """
        Check if DataFrame is empty.
        
        Args:
            data: DataFrame to check
            
        Returns:
            True if DataFrame is empty or None
        """
        if data is None:
            return True
        return data.empty
    
    def row_count(self, data: Optional[pd.DataFrame]) -> int:
        """
        Get number of rows in DataFrame.
        
        Args:
            data: DataFrame
            
        Returns:
            Number of rows
        """
        if data is None:
            return 0
        return len(data)
    
    def column_count(self, data: Optional[pd.DataFrame]) -> int:
        """
        Get number of columns in DataFrame.
        
        Args:
            data: DataFrame
            
        Returns:
            Number of columns
        """
        if data is None:
            return 0
        return len(data.columns)
    
    def get_columns(self, data: Optional[pd.DataFrame]) -> List[str]:
        """
        Get column names from DataFrame.
        
        Args:
            data: DataFrame
            
        Returns:
            List of column names
        """
        if data is None:
            return []
        return list(data.columns)
    
    def select_columns(self, data: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Select specific columns from DataFrame.
        
        Args:
            data: DataFrame
            columns: List of column names to select
            
        Returns:
            DataFrame with only selected columns
            
        Raises:
            KeyError: If columns don't exist
        """
        try:
            return data[columns]
        except KeyError as e:
            missing = [col for col in columns if col not in data.columns]
            raise KeyError(f"Columns not found: {missing}")
    
    def filter_rows(self, data: pd.DataFrame, conditions: Dict[str, Any]) -> pd.DataFrame:
        """
        Filter DataFrame rows based on conditions.
        
        Args:
            data: DataFrame to filter
            conditions: Dictionary of column:value pairs
            
        Returns:
            Filtered DataFrame
        """
        if not conditions:
            return data
        
        # Start with all True mask
        mask = pd.Series([True] * len(data), index=data.index)
        
        # Apply each condition
        for column, value in conditions.items():
            if column in data.columns:
                mask &= (data[column] == value)
        
        return data[mask]