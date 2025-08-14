"""
Rule Engine
Orchestrates rule execution and validation
"""
from typing import List, Dict, Any, Optional
import pandas as pd
from src.core.interfaces import (
    IRule, 
    IRuleProvider, 
    ValidationContext, 
    ValidationError,
    IValidator
)


class RuleEngine(IValidator):
    """
    Engine that executes validation rules
    """
    
    def __init__(self, name: str = "RuleEngine"):
        self.name = name
        self.rules: List[IRule] = []
        self.providers: List[IRuleProvider] = []
    
    def add_rule(self, rule: IRule) -> None:
        """Add a single rule to the engine"""
        self.rules.append(rule)
    
    def add_provider(self, provider: IRuleProvider) -> None:
        """Add a rule provider"""
        self.providers.append(provider)
    
    def get_name(self) -> str:
        """Get engine name"""
        return self.name
    
    def get_priority(self) -> int:
        """Rule engine has default priority"""
        return 100
    
    def validate(self, data: pd.DataFrame, context: Dict[str, Any]) -> List[ValidationError]:
        """
        Validate dataframe using all registered rules
        
        Args:
            data: DataFrame to validate
            context: Additional context (marketplace, category, etc)
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Collect all rules from providers
        all_rules = list(self.rules)
        for provider in self.providers:
            all_rules.extend(provider.get_rules())
        
        # Iterate through each row
        for row_idx, row in data.iterrows():
            # Convert row index to 1-based (accounting for header)
            # row_idx is 0-based, we want 1-based counting from first data row
            row_number = row_idx + 1  # Data row number (first data row = 1)
            
            # Validate each column
            for column_name in data.columns:
                value = row[column_name]
                
                # Create validation context
                validation_context = ValidationContext(
                    marketplace=context.get('marketplace', ''),
                    category=context.get('category', ''),
                    row_index=row_number,
                    column_name=column_name,
                    row_data=row.to_dict(),
                    metadata=context
                )
                
                # Apply all applicable rules
                for rule in all_rules:
                    if rule.can_apply(validation_context):
                        error = rule.validate(value, validation_context)
                        if error:
                            errors.append(error)
        
        return errors
    
    def clear_rules(self) -> None:
        """Clear all rules"""
        self.rules.clear()
    
    def clear_providers(self) -> None:
        """Clear all providers"""
        self.providers.clear()