"""
Use case for CSV validation.
Handles domain logic without I/O concerns.
"""

import io
import time
import uuid
from ..core.logging_config import get_logger
from typing import Optional, Dict, Any
from dataclasses import dataclass
import pandas as pd

from .base import UseCase
from ..pipeline.validation_pipeline_decoupled import ValidationPipelineDecoupled
from ..utils import DataFrameUtils
from ...infrastructure.validators.rule_engine_validator import RuleEngineValidator
from ...services.rule_engine_service import RuleEngineService
from ...schemas.validate import (
    ValidationResult,
    Marketplace,
    Category
)

logger = get_logger(__name__)


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
    
    def __init__(
        self, 
        validation_pipeline: ValidationPipelineDecoupled = None,
        rule_engine_service: Optional[RuleEngineService] = None
    ):
        """
        Initialize the use case with optional dependencies.
        
        Args:
            validation_pipeline: Optional custom validation pipeline
            rule_engine_service: Optional RuleEngineService for dependency injection
        """
        if validation_pipeline is None:
            # Use injected RuleEngineService or create default if not provided
            if rule_engine_service is None:
                rule_engine_service = RuleEngineService()
            validator = RuleEngineValidator(rule_engine_service)
            validation_pipeline = ValidationPipelineDecoupled(validator)
        self.validation_pipeline = validation_pipeline
    
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
            
            # Clean data using shared utility (required: pipeline doesn't clean data)
            df = DataFrameUtils.clean_dataframe(df)
            
            # Validate using pipeline with job_id (now async)
            result = await self.validation_pipeline.validate(
                df=df,
                marketplace=input_data.marketplace,
                category=input_data.category,
                auto_fix=input_data.auto_fix,
                job_id=input_data.job_id
            )
            
            # Convert corrected DataFrame to dict using shared utility
            if result.corrected_data is not None:
                result.corrected_data = DataFrameUtils.dataframe_to_dict(result.corrected_data)
            
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
    
