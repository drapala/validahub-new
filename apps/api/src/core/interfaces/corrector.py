"""
Corrector Interface Definitions
Defines the contracts for correctors and correction strategies
"""
from abc import ABC, abstractmethod
from typing import Any, Optional, List, Dict
from .rule import ValidationError


class ICorrection(ABC):
    """Base interface for corrections"""
    
    @abstractmethod
    def can_correct(self, error: ValidationError) -> bool:
        """
        Check if this correction can handle the given error
        
        Args:
            error: The validation error
            
        Returns:
            True if this correction can handle the error
        """
        pass
    
    @abstractmethod
    def apply(self, value: Any, error: ValidationError, context: Dict[str, Any]) -> Any:
        """
        Apply correction to a value
        
        Args:
            value: The incorrect value
            error: The validation error
            context: Additional context
            
        Returns:
            The corrected value
        """
        pass
    
    @abstractmethod
    def get_priority(self) -> int:
        """
        Get correction priority (lower applies first)
        
        Returns:
            Priority value (default 100)
        """
        return 100


class ICorrectionStrategy(ABC):
    """Interface for correction strategies"""
    
    @abstractmethod
    def add_correction(self, correction: ICorrection) -> None:
        """Add a correction to the strategy"""
        pass
    
    @abstractmethod
    def remove_correction(self, correction_type: str) -> None:
        """Remove a correction by type"""
        pass
    
    @abstractmethod
    def apply_corrections(
        self, 
        errors: List[ValidationError], 
        data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply all applicable corrections
        
        Args:
            errors: List of validation errors
            data: The data to correct
            context: Additional context
            
        Returns:
            Corrected data with metadata about corrections applied
        """
        pass


class ICorrectionProvider(ABC):
    """Interface for components that provide corrections"""
    
    @abstractmethod
    def get_corrections(self) -> List[ICorrection]:
        """Get all corrections from this provider"""
        pass
    
    @abstractmethod
    def get_correction_for_error(self, error: ValidationError) -> Optional[ICorrection]:
        """Get the best correction for a specific error"""
        pass