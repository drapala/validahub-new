"""
Base class for rule providers with caching support
"""
from typing import Dict, List, Optional, Any
from abc import abstractmethod
from src.core.interfaces import IRuleProvider, IRule


class CachedRuleProvider(IRuleProvider):
    """
    Base class that implements caching for rule providers.
    Subclasses only need to implement _get_rules_with_context()
    """
    
    def __init__(self):
        """Initialize caches"""
        self._rules_cache = None
        self._rule_id_map = None
    
    def get_rules(self) -> Dict[str, List[IRule]]:
        """
        Returns validation rules with caching.
        Calls _get_rules_with_context() only once and caches the result.
        """
        if self._rules_cache is None:
            self._rules_cache = self._get_rules_with_context({})
        return self._rules_cache
    
    def get_rule_by_id(self, rule_id: str) -> Optional[IRule]:
        """
        Returns a rule by its ID with caching for performance.
        Builds a rule_id -> rule map on first call.
        """
        if self._rule_id_map is None:
            self._rule_id_map = {}
            rules = self.get_rules()
            for field_rules in rules.values():
                for rule in field_rules:
                    rid = getattr(rule, 'rule_id', None)
                    if rid is not None:
                        self._rule_id_map[rid] = rule
        return self._rule_id_map.get(rule_id)
    
    @abstractmethod
    def _get_rules_with_context(self, context: Dict[str, Any]) -> Dict[str, List[IRule]]:
        """
        Internal method that generates rules based on context.
        Must be implemented by subclasses.
        
        Args:
            context: Context dictionary with marketplace/category info
            
        Returns:
            Dictionary mapping column names to lists of rules
        """
        pass
    
    def clear_cache(self):
        """
        Clear all caches. Useful for testing or when rules need to be refreshed.
        """
        self._rules_cache = None
        self._rule_id_map = None