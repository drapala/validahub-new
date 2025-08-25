"""Tabular data reader port."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, AsyncIterator, Dict, List, Optional


@dataclass
class TabularMetadata:
    """Metadata for tabular data."""
    
    row_count: int
    column_count: int
    columns: List[str]
    estimated_size_bytes: Optional[int] = None
    detected_delimiter: Optional[str] = None
    has_header: bool = True


class TabularReaderPort(ABC):
    """
    Port for reading tabular data (CSV, Excel, etc).
    Abstracts away pandas/polars/other implementations.
    """
    
    @abstractmethod
    async def read_metadata(self, source: Any) -> TabularMetadata:
        """
        Read metadata without loading all data.
        
        Args:
            source: Data source (file path, stream, etc)
            
        Returns:
            TabularMetadata instance
        """
        pass
    
    @abstractmethod
    async def read_rows(
        self,
        source: Any,
        skip_rows: int = 0,
        limit: Optional[int] = None,
        columns: Optional[List[str]] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Read rows as dictionaries.
        
        Args:
            source: Data source
            skip_rows: Number of rows to skip
            limit: Maximum rows to read
            columns: Specific columns to read
            
        Yields:
            Row dictionaries
        """
        pass
    
    @abstractmethod
    async def read_batch(
        self,
        source: Any,
        batch_size: int = 1000,
        skip_rows: int = 0
    ) -> AsyncIterator[List[Dict[str, Any]]]:
        """
        Read rows in batches for efficient processing.
        
        Args:
            source: Data source
            batch_size: Rows per batch
            skip_rows: Initial rows to skip
            
        Yields:
            Batches of row dictionaries
        """
        pass
    
    @abstractmethod
    async def validate_format(self, source: Any) -> bool:
        """
        Validate if source is readable.
        
        Args:
            source: Data source to validate
            
        Returns:
            True if format is valid and readable
        """
        pass
    
    @abstractmethod
    async def detect_types(
        self,
        source: Any,
        sample_size: int = 100
    ) -> Dict[str, str]:
        """
        Detect column data types.
        
        Args:
            source: Data source
            sample_size: Rows to sample for detection
            
        Returns:
            Mapping of column names to detected types
        """
        pass