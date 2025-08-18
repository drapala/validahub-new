"""
Use case for single row validation.
Handles domain logic for row-level validation.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from .base import UseCase
from ..pipeline.validation_pipeline_decoupled import ValidationPipelineDecoupled
from ...infrastructure.validators.rule_engine_validator import RuleEngineValidator
from ...services.rule_engine_service import RuleEngineService
from ...schemas.validate import (
    ValidationItem,
    ValidationStatus,
    Marketplace,
    Category
)

logger = logging.getLogger(__name__)


@dataclass
class ValidateRowInput:
    """Input data for row validation use case."""
    row_data: Dict[str, Any]
    marketplace: Marketplace
    category: Optional[Category] = None
    row_number: int = 1
    auto_fix: bool = True


@dataclass
class ValidateRowOutput:
    """Output data for row validation use case."""
    original_row: Dict[str, Any]
    fixed_row: Optional[Dict[str, Any]]
    validation_items: List[Dict[str, Any]]
    has_errors: bool
    has_warnings: bool
    auto_fix_applied: bool


class ValidateRowUseCase(UseCase[ValidateRowInput, ValidateRowOutput]):
    """
    Use case for validating a single row.
    
    This class handles the core business logic of row validation
    without any knowledge of HTTP or other infrastructure concerns.
    """
    
    def __init__(self, validation_pipeline: ValidationPipelineDecoupled = None):
        if validation_pipeline is None:
            # Create default pipeline with RuleEngineValidator
            rule_engine = RuleEngineService()
            validator = RuleEngineValidator(rule_engine)
            validation_pipeline = ValidationPipelineDecoupled(validator)
        self.validation_pipeline = validation_pipeline
    
    async def execute(self, input_data: ValidateRowInput) -> ValidateRowOutput:
        """
        Execute row validation logic.
        
        Args:
            input_data: Validated input containing row data and parameters
            
        Returns:
            ValidateRowOutput with validation results
            
        Raises:
            Exception: For processing errors
        """
        try:
            # Validate single row (now async)
            fixed_row, validation_items = await self.validation_pipeline.validate_single_row(
                row=input_data.row_data,
                marketplace=input_data.marketplace,
                category=input_data.category,
                row_number=input_data.row_number,
                auto_fix=input_data.auto_fix
            )
            
            # Determine if there are errors or warnings
            has_errors = any(item.status == ValidationStatus.ERROR for item in validation_items)
            has_warnings = any(item.status == ValidationStatus.WARNING for item in validation_items)
            
            # Convert validation items to dict
            items_dict = [item.model_dump() for item in validation_items]
            
            return ValidateRowOutput(
                original_row=input_data.row_data,
                fixed_row=fixed_row if input_data.auto_fix else None,
                validation_items=items_dict,
                has_errors=has_errors,
                has_warnings=has_warnings,
                auto_fix_applied=input_data.auto_fix
            )
            
        except Exception as e:
            logger.exception(f"Error validating row: {e}")
            raise