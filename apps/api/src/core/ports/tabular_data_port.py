"""
Port interface for tabular data operations.

This interface defines the contract for handling tabular data
without depending on any specific implementation (pandas, polars, etc).
"""

from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional, Union
from io import StringIO


class TabularDataPort(ABC):
    """
    Abstract interface for tabular data operations.
    
    This port defines operations needed by the core domain
    without specifying implementation details.
    """
    
    @abstractmethod
    def parse_csv(self, csv_content: Union[str, StringIO]) -> Any:
        """
        Parse CSV content into tabular data structure.
        
        Args:
            csv_content: CSV content as string or file-like object
            
        Returns:
            Tabular data structure (implementation-specific)
            
        Raises:
            ValueError: If CSV parsing fails
        """
        pass
    
    @abstractmethod
    def clean_data(self, data: Any) -> Any:
        """
        Clean tabular data by handling special values.
        
        Should handle:
        - NaN/null values
        - Infinity values
        - Data type conversions
        
        Args:
            data: Tabular data to clean
            
        Returns:
            Cleaned tabular data
        """
        pass
    
    @abstractmethod
    def to_dict_records(self, data: Any) -> List[Dict[str, Any]]:
        """
        Convert tabular data to list of dictionaries.
        
        Args:
            data: Tabular data structure
            
        Returns:
            List of dictionaries, each representing a row
        """
        pass
    
    @abstractmethod
    def to_csv_string(self, data: Any) -> str:
        """
        Convert tabular data to CSV string.
        
        Args:
            data: Tabular data structure
            
        Returns:
            CSV formatted string
        """
        pass
    
    @abstractmethod
    def is_empty(self, data: Any) -> bool:
        """
        Check if tabular data is empty.
        
        Args:
            data: Tabular data structure
            
        Returns:
            True if data is empty or None
        """
        pass
    
    @abstractmethod
    def row_count(self, data: Any) -> int:
        """
        Get number of rows in tabular data.
        
        Args:
            data: Tabular data structure
            
        Returns:
            Number of rows
        """
        pass
    
    @abstractmethod
    def column_count(self, data: Any) -> int:
        """
        Get number of columns in tabular data.
        
        Args:
            data: Tabular data structure
            
        Returns:
            Number of columns
        """
        pass
    
    @abstractmethod
    def get_columns(self, data: Any) -> List[str]:
        """
        Get column names from tabular data.
        
        Args:
            data: Tabular data structure
            
        Returns:
            List of column names
        """
        pass
    
    @abstractmethod
    def select_columns(self, data: Any, columns: List[str]) -> Any:
        """
        Select specific columns from tabular data.
        
        Args:
            data: Tabular data structure
            columns: List of column names to select
            
        Returns:
            Tabular data with only selected columns
            
        Raises:
            KeyError: If columns don't exist
        """
        pass
    
    @abstractmethod
    def filter_rows(self, data: Any, conditions: Dict[str, Any]) -> Any:
        """
        Filter rows based on conditions.
        
        Args:
            data: Tabular data structure
            conditions: Dictionary of column:value pairs for filtering
            
        Returns:
            Filtered tabular data
        """
        pass