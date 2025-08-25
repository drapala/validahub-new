import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any

from core.interfaces.dataframe_adapter import IDataFrameAdapter


class DataFrameUtils(IDataFrameAdapter):
    """Utility class for DataFrame operations."""

    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean DataFrame by handling NaN and inf values."""
        # Explicitly immutable operations (inplace=False is default, but being explicit)
        df = df.replace([np.inf, -np.inf], None, inplace=False)
        df = df.where(pd.notnull(df), None, inplace=False)
        return df

    def dataframe_to_dict(self, df: Optional[pd.DataFrame]) -> Optional[List[Dict[str, Any]]]:
        """Convert DataFrame to dictionary format for JSON serialization."""
        if df is None:
            return None
        df = self.clean_dataframe(df)
        return df.to_dict('records')

    def dataframe_to_csv(self, df: Optional[pd.DataFrame]) -> Optional[str]:
        """Convert DataFrame to CSV string."""
        if df is None:
            return None
        df = self.clean_dataframe(df)
        return df.to_csv(index=False)
