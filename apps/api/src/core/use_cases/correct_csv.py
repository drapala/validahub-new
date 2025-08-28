"""
Use case for CSV correction.
Handles domain logic for automatic CSV corrections.
"""

import uuid
from src.core.logging_config import get_logger
from typing import Any, Dict, Optional
from dataclasses import dataclass

from .base import UseCase
from ..pipeline.validation_pipeline_decoupled import ValidationPipelineDecoupled
from ..utils import DataFrameUtils
from ..ports.tabular_data_port import TabularDataPort
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
    
    def __init__(
        self,
        validation_pipeline: ValidationPipelineDecoupled,
        tabular_adapter: TabularDataPort
    ):
        """
        Initialize the use case with required dependencies.
        
        Args:
            validation_pipeline: Pipeline for validation logic
            tabular_adapter: Adapter for tabular data operations
        """
        self.validation_pipeline = validation_pipeline
        self.data_utils = DataFrameUtils(tabular_adapter)
    
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
        import time
        start_time = time.time()
        
        try:
            # Parse CSV using adapter (no direct pandas usage)
            data = self.data_utils.parse_csv(input_data.csv_content)
            
            # Clean data using adapter
            data = self.data_utils.clean_dataframe(data)
            
            # Validate and fix using pipeline with job_id (now async)
            job_id = str(uuid.uuid4())
            result = await self.validation_pipeline.validate(
                df=data,
                marketplace=input_data.marketplace,
                category=input_data.category,
                auto_fix=True,  # Always fix for correction use case
                job_id=job_id
            )
            
            # Convert corrected data to CSV using adapter
            corrected_csv = self.data_utils.dataframe_to_csv(result.corrected_data)
            if corrected_csv is None:
                # If no corrections, return original
                corrected_csv = input_data.csv_content
            
            return CorrectCsvOutput(
                corrected_csv=corrected_csv,
                original_filename=input_data.original_filename,
                total_corrections=result.summary.total_corrections,
                total_errors=result.summary.total_errors,
                total_warnings=result.summary.total_warnings,
                processing_time=time.time() - start_time,
                job_id=job_id
            )
            
        except ValueError as e:
            # Re-raise ValueError from adapter
            raise
        except Exception as e:
            logger.exception(f"Error correcting CSV: {e}")
            raise