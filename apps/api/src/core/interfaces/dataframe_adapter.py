"""DataFrame adapter interface for conversion and cleaning operations."""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import pandas as pd


class IDataFrameAdapter(ABC):
    """Interface for DataFrame conversion and cleaning."""

    @abstractmethod
    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean DataFrame by handling NaN and inf values."""
        pass

    @abstractmethod
    def dataframe_to_dict(self, df: Optional[pd.DataFrame]) -> Optional[List[Dict[str, Any]]]:
        """Convert DataFrame to a list of dictionaries."""
        pass

    @abstractmethod
    def dataframe_to_csv(self, df: Optional[pd.DataFrame]) -> Optional[str]:
        """Convert DataFrame to a CSV string."""
        pass
