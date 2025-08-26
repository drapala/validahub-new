"""
Use case for CSV validation.
Handles domain logic without I/O concerns.
"""

import uuid
from core.logging_config import get_logger
from typing import Any, Dict, Optional
from dataclasses import dataclass

from .base import UseCase
from ..pipeline.validation_pipeline_decoupled import ValidationPipelineDecoupled
from ..utils import DataFrameUtils
from ..ports.tabular_data_port import TabularDataPort
from ...schemas.validate import (
    Marketplace,
    Category,
    ValidationResult,
)

logger = get_logger(__name__)


@dataclass
class ValidateCsvInput:
    """Input data for CSV validation use case."""
    csv_content: str
    marketplace: Marketplace
    category: Category
    auto_fix: bool = True
    options: Optional[Dict[str, Any]] = None
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
            # Parse CSV using adapter (no direct pandas usage)
            data = self.data_utils.parse_csv(input_data.csv_content)
            
            # Clean data using adapter
            data = self.data_utils.clean_dataframe(data)
            
            # Validate using pipeline with job_id (now async)
            result = await self.validation_pipeline.validate(
                df=data,
                marketplace=input_data.marketplace,
                category=input_data.category,
                auto_fix=input_data.auto_fix,
                job_id=input_data.job_id
            )
            
            # Convert corrected DataFrame to dict using shared utility
            if result.corrected_data is not None:
                result.corrected_data = self.data_utils.dataframe_to_dict(result.corrected_data)
            
            return result
            
        except ValueError as e:
            # Re-raise ValueError from adapter
            raise
        except Exception as e:
            logger.exception(f"Error processing CSV: {e}")
            raise
    
    # Note: _parse_csv method removed - now using adapter