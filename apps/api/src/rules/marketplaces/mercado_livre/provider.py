"""
Mercado Livre Rules Provider
Provides all validation rules specific to Mercado Livre marketplace
"""
from typing import List, Optional
from src.core.interfaces import IRuleProvider, IRule
from src.rules.base.required_fields import RequiredFieldRule
from src.rules.base.text_rules import TextLengthRule
from src.rules.base.number_rules import PositiveNumberRule
from src.rules.base.stock_rules import StockQuantityRule


class MercadoLivreRuleProvider(IRuleProvider):
    """
    Provides validation rules for Mercado Livre marketplace
    """
    
    def __init__(self):
        self.rules = self._initialize_rules()
    
    def _initialize_rules(self) -> List[IRule]:
        """Initialize all Mercado Livre specific rules"""
        rules = []
        
        # Required fields for Mercado Livre
        rules.append(RequiredFieldRule(
            fields=['sku', 'title', 'price', 'available_quantity', 'condition'],
            rule_id='ml_required_fields'
        ))
        
        # Title constraints
        rules.append(TextLengthRule(
            field='title',
            max_length=60,
            min_length=10,
            rule_id='ml_title_length'
        ))
        
        # Price constraints
        rules.append(PositiveNumberRule(
            field='price',
            allow_zero=False,
            rule_id='ml_price_positive'
        ))
        
        # Stock constraints - use combined rule to avoid duplicates
        rules.append(StockQuantityRule(
            field='available_quantity',
            rule_id='ml_stock_quantity'
        ))
        
        return rules
    
    def get_rules(self) -> List[IRule]:
        """Get all rules from this provider"""
        return self.rules
    
    def get_rule_by_id(self, rule_id: str) -> Optional[IRule]:
        """Get a specific rule by ID"""
        for rule in self.rules:
            if rule.rule_id == rule_id:
                return rule
        return None
    
    def add_custom_rule(self, rule: IRule) -> None:
        """Add a custom rule to the provider"""
        self.rules.append(rule)
    
    def remove_rule(self, rule_id: str) -> None:
        """Remove a rule by ID"""
        self.rules = [r for r in self.rules if r.rule_id != rule_id]