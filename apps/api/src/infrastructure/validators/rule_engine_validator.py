"""
Improved adapter implementation for RuleEngineService as IValidator.
Bridges the existing rule engine with the new interface.
"""

import asyncio
import copy
import functools
from src.core.logging_config import get_logger
from typing import Any, Dict, List, Optional, Tuple

from src.core.interfaces.rule_engine import IRuleEngineService
from src.core.interfaces.validation import IValidator
from src.schemas.validate import ValidationItem

logger = get_logger(__name__)


class RuleEngineValidator(IValidator):
    """
    Adapter that implements IValidator using RuleEngineService.
    This allows the existing rule engine to work with the new pipeline.
    """
    
    def __init__(self, rule_engine_service: IRuleEngineService):
        """Initialize validator with rule engine service."""
        self.rule_engine_service = rule_engine_service
    
    async def validate_row(
        self,
        row: Dict[str, Any],
        marketplace: str,
        row_number: int = 0,
        context: Optional[Dict[str, Any]] = None
    ) -> List[ValidationItem]:
        """
        Validate a single row using rule engine.
        
        Args:
            row: Row data to validate
            marketplace: Target marketplace
            row_number: Row number for reporting
            context: Additional validation context (unused currently)
            
        Returns:
            List of validation items
        
        Raises:
            RuntimeError: If the rule engine service is not properly configured
        """
        try:
            # Check if service has async method
            if hasattr(self.rule_engine_service, 'validate_row') and callable(self.rule_engine_service.validate_row):
                # Use sync method for backward compatibility
                if asyncio.iscoroutinefunction(self.rule_engine_service.validate_row):
                    return await self.rule_engine_service.validate_row(
                        row=row, 
                        marketplace=marketplace, 
                        row_number=row_number
                    )
                else:
                    # Wrap sync call in executor for non-blocking execution
                    loop = asyncio.get_event_loop()
                    func = functools.partial(
                        self.rule_engine_service.validate_row,
                        row=row,
                        marketplace=marketplace,
                        row_number=row_number
                    )
                    return await loop.run_in_executor(None, func)
            else:
                # Direct call for concrete implementation
                return self.rule_engine_service.validate_row(
                    row=row, 
                    marketplace=marketplace, 
                    row_number=row_number
                )
        except Exception as e:
            logger.error(f"Error validating row {row_number}: {str(e)}")
            raise RuntimeError(f"Validation failed for row {row_number}: {str(e)}") from e
    
    async def validate_and_fix_row(
        self,
        row: Dict[str, Any],
        marketplace: str,
        row_number: int = 0,
        auto_fix: bool = True,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, Any], List[ValidationItem]]:
        """
        Validate and optionally fix a row.
        
        Args:
            row: Row data to validate and fix
            marketplace: Target marketplace
            row_number: Row number for reporting
            auto_fix: Whether to apply fixes
            context: Additional validation context (unused currently)
            
        Returns:
            Tuple of (fixed_row, validation_items)
            
        Raises:
            RuntimeError: If the rule engine service is not properly configured
        """
        # Preserve original row to avoid mutations
        row_copy = copy.deepcopy(row)
        
        try:
            # Check if service has async method
            if hasattr(self.rule_engine_service, 'validate_and_fix_row'):
                if asyncio.iscoroutinefunction(self.rule_engine_service.validate_and_fix_row):
                    return await self.rule_engine_service.validate_and_fix_row(
                        row=row_copy, 
                        marketplace=marketplace, 
                        row_number=row_number, 
                        auto_fix=auto_fix
                    )
                else:
                    # Wrap sync call in executor for non-blocking execution
                    loop = asyncio.get_event_loop()
                    func = functools.partial(
                        self.rule_engine_service.validate_and_fix_row,
                        row=row_copy,
                        marketplace=marketplace,
                        row_number=row_number,
                        auto_fix=auto_fix
                    )
                    return await loop.run_in_executor(None, func)
            else:
                # Direct call for concrete implementation
                return self.rule_engine_service.validate_and_fix_row(
                    row=row_copy, 
                    marketplace=marketplace, 
                    row_number=row_number, 
                    auto_fix=auto_fix
                )
        except Exception as e:
            logger.error(f"Error validating and fixing row {row_number}: {str(e)}")
            raise RuntimeError(f"Validation and fix failed for row {row_number}: {str(e)}") from e


class MultiStrategyValidator(IValidator):
    """
    Validator that can use multiple validation strategies.
    Allows combining rule engine with other validators.
    """
    
    def __init__(self, validators: List[IValidator]):
        """
        Initialize with multiple validators.
        
        Args:
            validators: List of validators to use
        """
        self.validators = validators
    
    async def validate_row(
        self,
        row: Dict[str, Any],
        marketplace: str,
        row_number: int = 0,
        context: Optional[Dict[str, Any]] = None
    ) -> List[ValidationItem]:
        """
        Validate using all validators and combine results.
        
        Args:
            row: Row data to validate
            marketplace: Target marketplace
            row_number: Row number for reporting
            context: Additional validation context
            
        Returns:
            Combined validation items from all validators
        """
        all_items = []
        
        for validator in self.validators:
            items = await validator.validate_row(row, marketplace, row_number, context)
            all_items.extend(items)
        
        # Deduplicate if needed
        return self._deduplicate_items(all_items)
    
    async def validate_and_fix_row(
        self,
        row: Dict[str, Any],
        marketplace: str,
        row_number: int = 0,
        auto_fix: bool = True,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, Any], List[ValidationItem]]:
        """
        Validate and fix using all validators.
        
        Args:
            row: Row data to validate and fix
            marketplace: Target marketplace
            row_number: Row number for reporting
            auto_fix: Whether to apply fixes
            context: Additional validation context
            
        Returns:
            Tuple of (fixed_row, validation_items)
            
        Note:
            When multiple validators fix the same field, the first validator's
            fix takes precedence. This prevents later validators from overwriting
            earlier fixes.
        """
        original_row = copy.deepcopy(row)
        fixed_row = copy.deepcopy(row)
        all_items = []
        
        for validator in self.validators:
            validator_fixed_row, items = await validator.validate_and_fix_row(
                fixed_row, marketplace, row_number, auto_fix, context
            )
            
            if auto_fix:
                # Apply fixes from this validator only for fields not already fixed
                for key, value in validator_fixed_row.items():
                    # Only update if the field in fixed_row is still the same as in the original row
                    # This ensures the first validator's fix takes precedence
                    if fixed_row.get(key) == original_row.get(key) and value != original_row.get(key):
                        fixed_row[key] = value
            
            all_items.extend(items)
        
        return fixed_row, self._deduplicate_items(all_items)
    
    def _deduplicate_items(self, items: List[ValidationItem]) -> List[ValidationItem]:
        """
        Remove duplicate validation items.
        
        Args:
            items: List of validation items
            
        Returns:
            Deduplicated list
        """
        seen = set()
        unique_items = []
        
        for item in items:
            # Create a key for deduplication
            key = (
                item.row_number,
                item.status,
                tuple(e.field for e in item.errors) if item.errors else (),
                tuple(c.field for c in item.corrections) if item.corrections else ()
            )
            
            if key not in seen:
                seen.add(key)
                unique_items.append(item)
        
        return unique_items