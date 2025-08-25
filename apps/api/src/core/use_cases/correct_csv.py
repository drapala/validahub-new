"""
Use case for CSV correction.
Handles domain logic for automatic CSV corrections.
"""

import io
import uuid
from core.logging_config import get_logger
from typing import Any, Dict, Optional
from dataclasses import dataclass
import pandas as pd

from .base import UseCase
from ..pipeline.validation_pipeline_decoupled import ValidationPipelineDecoupled
from utils import DataFrameUtils
from ...schemas.validate import (
    Category,
    Marketplace,
)

logger = get_logger(__name__)


@dataclass
class CorrectCsvInput:
    """Input data for CSV correction use case."""
    csv_content: str
    marketplace: Marketplace
    category: Category
    options: Optional[Dict[str, Any]] = None
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
    
    def __init__(self, validation_pipeline: ValidationPipelineDecoupled):
        """Initialize the use case with required validation pipeline."""
        self.validation_pipeline = validation_pipeline
    
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
            
            # Clean data using shared utility (required: pipeline doesn't clean data)
            df = DataFrameUtils.clean_dataframe(df)
            
            # Validate and fix using pipeline with job_id (now async)
            job_id = str(uuid.uuid4())
            result = await self.validation_pipeline.validate(
                df=df,
                marketplace=input_data.marketplace,
                category=input_data.category,
                auto_fix=True,  # Always fix for correction use case
                job_id=job_id
            )
            
            # Convert corrected DataFrame to CSV using shared utility
            corrected_csv = DataFrameUtils.dataframe_to_csv(result.corrected_data)
            if corrected_csv is None:
                # If no corrections, return original
                corrected_csv = input_data.csv_content
            
            return CorrectCsvOutput(
                corrected_csv=corrected_csv,
                original_filename=input_data.original_filename,
                total_corrections=result.summary.total_corrections,
                total_errors=result.summary.total_errors,
                total_warnings=result.summary.total_warnings,
                processing_time=result.summary.processing_time_seconds,
                job_id=job_id
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
    
