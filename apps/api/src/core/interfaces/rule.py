"""
Rule Interface Definitions
Defines the contracts for validation rules and rule providers
"""
from abc import ABC, abstractmethod
from typing import Any, Optional, List, Dict
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    """Severity levels for validation errors"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationContext:
    """Context passed to rules during validation"""
    marketplace: str
    category: str
    row_index: int
    column_name: str
    row_data: Dict[str, Any]
    metadata: Dict[str, Any] = None


@dataclass
class ValidationError:
    """Represents a validation error"""
    row: int
    column: str
    error: str
    value: Any
    suggestion: Optional[str] = None
    severity: Severity = Severity.ERROR
    rule_id: Optional[str] = None


class IRule(ABC):
    """Base interface for all validation rules"""
    
    def __init__(self, rule_id: str = None):
        self.rule_id = rule_id or self.__class__.__name__
    
    @abstractmethod
    def validate(self, value: Any, context: ValidationContext) -> Optional[ValidationError]:
        """
        Validate a single value
        
        Args:
            value: The value to validate
            context: Context information for validation
            
        Returns:
            ValidationError if validation fails, None if passes
        """
        pass
    
    @abstractmethod
    def can_apply(self, context: ValidationContext) -> bool:
        """
        Check if this rule applies to the given context
        
        Args:
            context: Context to check
            
        Returns:
            True if rule should be applied
        """
        pass


class ICompositeRule(IRule):
    """Interface for rules that compose multiple sub-rules"""
    
    @abstractmethod
    def add_rule(self, rule: IRule) -> None:
        """Add a sub-rule"""
        pass
    
    @abstractmethod
    def remove_rule(self, rule_id: str) -> None:
        """Remove a sub-rule by ID"""
        pass


class IRuleProvider(ABC):
    """Interface for components that provide rules"""
    
    @abstractmethod
    def get_rules(self) -> Dict[str, List[IRule]]:
        """
        Get all rules from this provider
        
        Returns:
            Dictionary mapping column names to lists of rules
        """
        pass
    
    @abstractmethod
    def get_rule_by_id(self, rule_id: str) -> Optional[IRule]:
        """Get a specific rule by ID"""
        pass


class IRuleRegistry(ABC):
    """Interface for the central rule registry"""
    
    @abstractmethod
    def register_rule(self, rule_type: str, rule_class: type) -> None:
        """Register a rule type"""
        pass
    
    @abstractmethod
    def create_rule(self, rule_type: str, **kwargs) -> IRule:
        """Create a rule instance"""
        pass
    
    @abstractmethod
    def list_rule_types(self) -> List[str]:
        """List all registered rule types"""
        pass