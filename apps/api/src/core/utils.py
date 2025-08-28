"""
Shared utilities for use cases.
"""

from typing import Optional, List, Dict, Any
from src.core.ports.tabular_data_port import TabularDataPort


class DataFrameUtils:
    """
    Utility class for tabular data operations.
    
    This class uses the TabularDataPort abstraction to perform
    operations without depending on any specific implementation.
    """
    
    def __init__(self, tabular_adapter: TabularDataPort):
        """
        Initialize with a tabular data adapter.
        
        Args:
            tabular_adapter: Concrete implementation of TabularDataPort
        """
        self.adapter = tabular_adapter
    
    def parse_csv(self, csv_content: str) -> Any:
        """
        Parse CSV string to tabular data.
        
        Args:
            csv_content: CSV content as string
            
        Returns:
            Tabular data structure
            
        Raises:
            ValueError: If parsing fails
        """
        return self.adapter.parse_csv(csv_content)
    
    def clean_dataframe(self, data: Any) -> Any:
        """
        Clean tabular data by handling special values.
        
        Args:
            data: Tabular data to clean
            
        Returns:
            Cleaned tabular data
        """
        return self.adapter.clean_data(data)
    
    def dataframe_to_dict(self, data: Optional[Any]) -> Optional[List[Dict[str, Any]]]:
        """
        Convert tabular data to dictionary format for JSON serialization.
        
        Args:
            data: Tabular data to convert
            
        Returns:
            List of dictionaries representing rows, or None if data is None
        """
        if data is None:
            return None
        return self.adapter.to_dict_records(data)
    
    def dataframe_to_csv(self, data: Optional[Any]) -> Optional[str]:
        """
        Convert tabular data to CSV string.
        
        Args:
            data: Tabular data to convert
            
        Returns:
            CSV string or None if data is None
        """
        if data is None:
            return None
        return self.adapter.to_csv_string(data)