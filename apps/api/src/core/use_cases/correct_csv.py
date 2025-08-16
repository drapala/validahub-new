"""
Use case for CSV correction.
Handles domain logic for automatic CSV corrections.
"""

import io
import uuid
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
import pandas as pd
import numpy as np

from .base import UseCase
from ..pipeline.validation_pipeline import ValidationPipeline
from ...schemas.validate import (
    Marketplace,
    Category
)

logger = logging.getLogger(__name__)


@dataclass
class CorrectCsvInput:
    """Input data for CSV correction use case."""
    csv_content: str
    marketplace: Marketplace
    category: Category
    options: Dict[str, Any] = None
    original_filename: str = "file.csv"
    
    def __post_init__(self):
        if self.options is None:
            self.options = {}


@dataclass
class CorrectCsvOutput:
    """Output data for CSV correction use case."""
    corrected_csv: str
    original_filename: str
    total_corrections: int
    total_errors: int
    total_warnings: int
    processing_time: float
    job_id: str


class CorrectCsvUseCase(UseCase[CorrectCsvInput, CorrectCsvOutput]):
    """
    Use case for correcting CSV data.
    
    This class handles the core business logic of CSV correction
    without any knowledge of HTTP, file I/O, or other infrastructure concerns.
    """
    
    def __init__(self, validation_pipeline: ValidationPipeline = None):
        self.validation_pipeline = validation_pipeline or ValidationPipeline()
    
    async def execute(self, input_data: CorrectCsvInput) -> CorrectCsvOutput:
        """
        Execute CSV correction logic.
        
        Args:
            input_data: Validated input containing CSV content and parameters
            
        Returns:
            CorrectCsvOutput with corrected CSV and metadata
            
        Raises:
            ValueError: If CSV parsing fails
            Exception: For other processing errors
        """
        try:
            # Parse CSV to DataFrame
            df = self._parse_csv(input_data.csv_content)
            
            # Clean data
            df = self._clean_dataframe(df)
            
            # Validate and fix using pipeline
            result = self.validation_pipeline.validate(
                df=df,
                marketplace=input_data.marketplace,
                category=input_data.category,
                auto_fix=True  # Always fix for correction use case
            )
            
            # Convert corrected DataFrame to CSV
            if result.corrected_data is not None:
                corrected_csv = result.corrected_data.to_csv(index=False)
            else:
                # If no corrections, return original
                corrected_csv = input_data.csv_content
            
            return CorrectCsvOutput(
                corrected_csv=corrected_csv,
                original_filename=input_data.original_filename,
                total_corrections=result.summary.total_corrections,
                total_errors=result.summary.total_errors,
                total_warnings=result.summary.total_warnings,
                processing_time=result.summary.processing_time_seconds,
                job_id=str(uuid.uuid4())
            )
            
        except pd.errors.EmptyDataError:
            raise ValueError("CSV file is empty or invalid")
        except Exception as e:
            logger.exception(f"Error correcting CSV: {e}")
            raise
    
    def _parse_csv(self, csv_content: str) -> pd.DataFrame:
        """Parse CSV string to DataFrame."""
        try:
            return pd.read_csv(io.StringIO(csv_content))
        except Exception as e:
            raise ValueError(f"Failed to parse CSV: {str(e)}")
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean DataFrame by handling NaN and inf values."""
        df = df.replace([np.inf, -np.inf], None)
        df = df.where(pd.notnull(df), None)
        return df