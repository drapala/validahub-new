import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any

from core.interfaces.dataframe_adapter import IDataFrameAdapter


class DataFrameUtils(IDataFrameAdapter):
    """Utility class for DataFrame operations."""

    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean DataFrame by handling NaN and inf values.

        Args:
            df: DataFrame to be cleaned.

        Returns:
            DataFrame with NaN and inf values replaced by ``None``.
        """
        df = df.replace([np.inf, -np.inf], None)
        df = df.where(pd.notnull(df), None)
        return df

    def dataframe_to_dict(self, df: Optional[pd.DataFrame]) -> Optional[List[Dict[str, Any]]]:
        """
        Convert DataFrame to dictionary format for JSON serialization.

        Args:
            df: DataFrame to convert.

        Returns:
            List of dictionaries representing the DataFrame rows, or ``None`` if ``df`` is ``None``.
        """
        if df is None:
            return None
        df = self.clean_dataframe(df)
        return df.to_dict("records")

    def dataframe_to_csv(self, df: Optional[pd.DataFrame]) -> Optional[str]:
        """
        Convert DataFrame to CSV string.

        Args:
            df: DataFrame to convert to CSV.

        Returns:
            CSV string representation of the DataFrame, or ``None`` if ``df`` is ``None``.
        """
        if df is None:
            return None
        df = self.clean_dataframe(df)
        return df.to_csv(index=False)
