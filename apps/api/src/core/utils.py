"""
Shared utilities for use cases.
"""

import pandas as pd
import numpy as np
from typing import Optional


class DataFrameUtils:
    """Utility class for DataFrame operations."""
    
    @staticmethod
    def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean DataFrame by handling NaN and inf values.
        
        Args:
            df: DataFrame to clean
            
        Returns:
            Cleaned DataFrame
        """
        df = df.replace([np.inf, -np.inf], None)
        df = df.where(pd.notnull(df), None)
        return df
    
    @staticmethod
    def dataframe_to_dict(df: pd.DataFrame) -> list:
        """
        Convert DataFrame to dictionary format for JSON serialization.
        
        Args:
            df: DataFrame to convert
            
        Returns:
            List of dictionaries representing rows
        """
        if df is None:
            return None
        
        # Clean the dataframe first
        df = DataFrameUtils.clean_dataframe(df)
        return df.to_dict('records')
    
    @staticmethod
    def dataframe_to_csv(df: Optional[pd.DataFrame]) -> Optional[str]:
        """
        Convert DataFrame to CSV string.
        
        Args:
            df: DataFrame to convert
            
        Returns:
            CSV string or None if DataFrame is None
        """
        if df is None:
            return None
        
        # Clean the dataframe first
        df = DataFrameUtils.clean_dataframe(df)
        return df.to_csv(index=False)