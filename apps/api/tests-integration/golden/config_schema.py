"""Golden test configuration schema."""

from typing import List, Optional
from pydantic import BaseModel, Field


class GoldenTestConfig(BaseModel):
    """Configuration for a golden test case."""
    
    # CSV parsing
    separator: str = ","
    decimal: str = "."
    encoding: str = "utf-8"
    
    # Comparison keys
    key_columns: List[str] = Field(default_factory=list)
    sort_by: List[str] = Field(default_factory=list)
    
    # Normalization
    float_tolerance: float = 1e-6
    trim_whitespace: bool = True
    casefold_text: bool = False
    normalize_floats: bool = True
    
    # Columns to ignore
    ignore_columns_in_diff: List[str] = Field(default_factory=list)
    
    # Report comparison
    report_ignore_keys: List[str] = Field(
        default_factory=lambda: ["run_id", "timestamp", "duration_ms"]
    )
    
    # Streaming
    chunk_size: Optional[int] = None  # None = load entire file
    
    class Config:
        """Pydantic config."""
        extra = "forbid"  # Fail on unknown fields