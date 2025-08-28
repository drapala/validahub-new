"""Validation service port."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from src.schemas.validation import ValidationResult


class ValidationServicePort(ABC):
    """
    Port for validation services.
    Defines the contract for validating data against rules/policies.
    """
    
    @abstractmethod
    async def validate_row(
        self,
        row_data: Dict[str, Any],
        policy_id: str,
        row_number: int,
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate a single row of data against a policy.
        
        Args:
            row_data: The data to validate
            policy_id: ID of the policy to use
            row_number: Row number for error reporting
            context: Optional validation context
            
        Returns:
            ValidationResult with errors if any
        """
        pass
    
    @abstractmethod
    async def validate_batch(
        self,
        rows: List[Dict[str, Any]],
        policy_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[ValidationResult]:
        """
        Validate multiple rows in batch.
        
        Args:
            rows: List of row data to validate
            policy_id: ID of the policy to use
            context: Optional validation context
            
        Returns:
            List of ValidationResults
        """
        pass
    
    @abstractmethod
    async def get_available_policies(self) -> List[Dict[str, Any]]:
        """
        Get list of available validation policies.
        
        Returns:
            List of policy metadata
        """
        pass
    
    @abstractmethod
    async def reload_policies(self) -> None:
        """Reload validation policies from source."""
        pass