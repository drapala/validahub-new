"""
Use case for CSV validation.
Handles domain logic without I/O concerns.
"""

import io
import time
import uuid
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
import pandas as pd
import numpy as np

from .base import UseCase
from ..pipeline.validation_pipeline import ValidationPipeline
from ...schemas.validate import (
    ValidationResult,
    Marketplace,
    Category
)

logger = logging.getLogger(__name__)


@dataclass
class ValidateCsvInput:
    """Input data for CSV validation use case."""
    csv_content: str
    marketplace: Marketplace
    category: Category
    auto_fix: bool = True
    options: Dict[str, Any] = None
    job_id: Optional[str] = None
    
    def __post_init__(self):
        if self.options is None:
            self.options = {}
        if self.job_id is None:
            self.job_id = str(uuid.uuid4())


class ValidateCsvUseCase(UseCase[ValidateCsvInput, ValidationResult]):
    """
    Use case for validating CSV data.
    
    This class handles the core business logic of CSV validation
    without any knowledge of HTTP, file I/O, or other infrastructure concerns.
    """
    
    def __init__(self, validation_pipeline: ValidationPipeline = None):
        self.validation_pipeline = validation_pipeline or ValidationPipeline()
    
    async def execute(self, input_data: ValidateCsvInput) -> ValidationResult:
        """
        Execute CSV validation logic.
        
        Args:
            input_data: Validated input containing CSV content and parameters
            
        Returns:
            ValidationResult with all validation details
            
        Raises:
            ValueError: If CSV parsing fails
            Exception: For other processing errors
        """
        try:
            # Parse CSV to DataFrame
            df = self._parse_csv(input_data.csv_content)
            
            # Clean data
            df = self._clean_dataframe(df)
            
            # Validate using pipeline
            result = self.validation_pipeline.validate(
                df=df,
                marketplace=input_data.marketplace,
                category=input_data.category,
                auto_fix=input_data.auto_fix
            )
            
            # Add job_id for tracking (immutably)
            result = result.model_copy(update={"job_id": input_data.job_id})
            
            # Convert corrected DataFrame to dict if present
            if result.corrected_data is not None:
                df = result.corrected_data
                df = self._clean_dataframe(df)
                result.corrected_data = df.to_dict('records')
            
            return result
            
        except pd.errors.EmptyDataError:
            raise ValueError("CSV file is empty or invalid")
        except Exception as e:
            logger.exception(f"Error processing CSV: {e}")
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