"""Rule engine port for business rules execution."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set


@dataclass
class RuleResult:
    """Result of rule execution."""
    
    passed: bool
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]


class RuleEnginePort(ABC):
    """
    Port for rule engine operations.
    Defines contract for executing business rules.
    """
    
    @abstractmethod
    async def execute_rule(
        self,
        rule_id: str,
        data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> RuleResult:
        """
        Execute a single rule against data.
        
        Args:
            rule_id: Identifier of the rule to execute
            data: Data to validate against the rule
            context: Optional execution context
            
        Returns:
            RuleResult with execution outcome
        """
        pass
    
    @abstractmethod
    async def execute_ruleset(
        self,
        ruleset_id: str,
        data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> RuleResult:
        """
        Execute a set of rules against data.
        
        Args:
            ruleset_id: Identifier of the ruleset
            data: Data to validate
            context: Optional execution context
            
        Returns:
            Aggregated RuleResult
        """
        pass
    
    @abstractmethod
    async def get_rule_metadata(self, rule_id: str) -> Dict[str, Any]:
        """
        Get metadata for a specific rule.
        
        Args:
            rule_id: Rule identifier
            
        Returns:
            Rule metadata including description, parameters, etc.
        """
        pass
    
    @abstractmethod
    async def list_available_rules(self) -> List[Dict[str, str]]:
        """
        List all available rules.
        
        Returns:
            List of rule summaries with id and name
        """
        pass
    
    @abstractmethod
    async def validate_rule_syntax(self, rule_definition: str) -> bool:
        """
        Validate rule definition syntax.
        
        Args:
            rule_definition: Rule definition to validate
            
        Returns:
            True if syntax is valid
        """
        pass