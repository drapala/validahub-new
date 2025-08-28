"""
Mapper to transform MELI-specific rules to Canonical Rule Model.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from src.core.logging_config import get_logger
from ..models.canonical_rule import (
    CanonicalRule,
    CanonicalRuleSet,
    RuleType,
    DataType,
    RuleSeverity,
    RuleCondition
)
from ..models.meli_models import (
    MeliRuleAttribute,
    MeliCategory,
    MeliItemValidationRule,
    MeliRuleSet
)

logger = get_logger(__name__)


class MeliToCanonicalMapper:
    """
    Maps MELI-specific rule formats to the Canonical Rule Model.
    
    This mapper handles:
    - Attribute type mapping
    - Rule type inference
    - Validation parameter extraction
    - Error message generation
    """
    
    # Map MELI value types to canonical data types
    TYPE_MAPPING = {
        "STRING": DataType.STRING,
        "TEXT": DataType.STRING,
        "NUMBER": DataType.FLOAT,
        "INTEGER": DataType.INTEGER,
        "NUMBER_UNIT": DataType.FLOAT,
        "BOOLEAN": DataType.BOOLEAN,
        "DATE": DataType.DATE,
        "LIST": DataType.ARRAY,
        "OBJECT": DataType.OBJECT
    }
    
    # Map MELI validation types to canonical rule types
    VALIDATION_TYPE_MAPPING = {
        "REQUIRED": RuleType.REQUIRED,
        "MIN_LENGTH": RuleType.MIN_LENGTH,
        "MAX_LENGTH": RuleType.MAX_LENGTH,
        "PATTERN": RuleType.PATTERN,
        "ALLOWED_VALUES": RuleType.ENUM,
        "MIN_VALUE": RuleType.MIN_VALUE,
        "MAX_VALUE": RuleType.MAX_VALUE,
        "CUSTOM": RuleType.CUSTOM
    }
    
    def __init__(self, marketplace_id: str = "MELI"):
        """
        Initialize mapper.
        
        Args:
            marketplace_id: Identifier for the marketplace
        """
        self.marketplace_id = marketplace_id
    
    def map_attribute_to_rules(self, attribute: MeliRuleAttribute) -> List[CanonicalRule]:
        """
        Map a single MELI attribute to canonical rules.
        
        Args:
            attribute: MELI attribute definition
            
        Returns:
            List of canonical rules derived from the attribute
        """
        rules = []
        base_rule_id = f"{self.marketplace_id}_{attribute.id}"
        
        # Map data type
        data_type = self.TYPE_MAPPING.get(
            attribute.value_type,
            DataType.STRING
        )
        
        # Create required rule if applicable
        if attribute.required:
            rules.append(CanonicalRule(
                id=f"{base_rule_id}_required",
                marketplace_id=self.marketplace_id,
                original_id=attribute.id,
                field_name=attribute.id,
                rule_type=RuleType.REQUIRED,
                data_type=data_type,
                params={},
                severity=RuleSeverity.ERROR,
                message=f"{attribute.name} is required",
                description=f"The field {attribute.name} must be provided",
                category="required_fields",
                tags=["mandatory", "meli"],
                metadata={
                    "original_name": attribute.name,
                    "meli_id": attribute.id
                }
            ))
        
        # Create length validation rules
        if attribute.value_min_length is not None:
            rules.append(CanonicalRule(
                id=f"{base_rule_id}_min_length",
                marketplace_id=self.marketplace_id,
                original_id=attribute.id,
                field_name=attribute.id,
                rule_type=RuleType.MIN_LENGTH,
                data_type=data_type,
                params={"min_length": attribute.value_min_length},
                severity=RuleSeverity.ERROR,
                message=f"{attribute.name} must have at least {attribute.value_min_length} characters",
                description=f"Minimum length validation for {attribute.name}",
                category="length_validation",
                tags=["validation", "meli"],
                metadata={
                    "original_name": attribute.name,
                    "meli_id": attribute.id
                }
            ))
        
        if attribute.value_max_length is not None:
            rules.append(CanonicalRule(
                id=f"{base_rule_id}_max_length",
                marketplace_id=self.marketplace_id,
                original_id=attribute.id,
                field_name=attribute.id,
                rule_type=RuleType.MAX_LENGTH,
                data_type=data_type,
                params={"max_length": attribute.value_max_length},
                severity=RuleSeverity.ERROR,
                message=f"{attribute.name} must have at most {attribute.value_max_length} characters",
                description=f"Maximum length validation for {attribute.name}",
                category="length_validation",
                tags=["validation", "meli"],
                metadata={
                    "original_name": attribute.name,
                    "meli_id": attribute.id
                }
            ))
        
        # Create pattern validation rule
        if attribute.value_pattern:
            rules.append(CanonicalRule(
                id=f"{base_rule_id}_pattern",
                marketplace_id=self.marketplace_id,
                original_id=attribute.id,
                field_name=attribute.id,
                rule_type=RuleType.PATTERN,
                data_type=data_type,
                params={"pattern": attribute.value_pattern},
                severity=RuleSeverity.ERROR,
                message=f"{attribute.name} does not match required format",
                description=f"Pattern validation for {attribute.name}",
                category="format_validation",
                tags=["validation", "pattern", "meli"],
                metadata={
                    "original_name": attribute.name,
                    "meli_id": attribute.id,
                    "pattern": attribute.value_pattern
                }
            ))
        
        # Create enum validation rule
        if attribute.allowed_values:
            rules.append(CanonicalRule(
                id=f"{base_rule_id}_enum",
                marketplace_id=self.marketplace_id,
                original_id=attribute.id,
                field_name=attribute.id,
                rule_type=RuleType.ENUM,
                data_type=data_type,
                params={"values": attribute.allowed_values},
                severity=RuleSeverity.ERROR,
                message=f"{attribute.name} must be one of the allowed values",
                description=f"Allowed values validation for {attribute.name}",
                category="value_validation",
                tags=["validation", "enum", "meli"],
                metadata={
                    "original_name": attribute.name,
                    "meli_id": attribute.id,
                    "allowed_values": attribute.allowed_values
                }
            ))
        
        return rules
    
    def map_validation_rule(self, validation: MeliItemValidationRule) -> Optional[CanonicalRule]:
        """
        Map a MELI validation rule to canonical format.
        
        Args:
            validation: MELI validation rule
            
        Returns:
            Canonical rule or None if mapping fails
        """
        rule_type = self.VALIDATION_TYPE_MAPPING.get(
            validation.validation_type,
            RuleType.CUSTOM
        )
        
        # Determine parameters based on validation type
        params = {}
        if validation.validation_type == "MIN_LENGTH":
            params["min_length"] = validation.validation_value
        elif validation.validation_type == "MAX_LENGTH":
            params["max_length"] = validation.validation_value
        elif validation.validation_type == "PATTERN":
            params["pattern"] = validation.validation_value
        elif validation.validation_type == "ALLOWED_VALUES":
            params["values"] = validation.validation_value
        elif validation.validation_type == "MIN_VALUE":
            params["min_value"] = validation.validation_value
        elif validation.validation_type == "MAX_VALUE":
            params["max_value"] = validation.validation_value
        elif validation.validation_value is not None:  # Preserve falsy values like 0 or ""
            params["value"] = validation.validation_value
        
        # Map severity
        severity_map = {
            "ERROR": RuleSeverity.ERROR,
            "WARNING": RuleSeverity.WARNING,
            "INFO": RuleSeverity.INFO
        }
        severity = severity_map.get(validation.severity, RuleSeverity.ERROR)
        
        return CanonicalRule(
            id=f"{self.marketplace_id}_validation_{uuid.uuid4().hex}",
            marketplace_id=self.marketplace_id,
            original_id=validation.attribute_id,
            field_name=validation.attribute_id,
            rule_type=rule_type,
            data_type=DataType.STRING,  # Default, should be enriched with attribute info
            params=params,
            severity=severity,
            message=validation.error_message,
            description=f"Validation rule for {validation.attribute_name}",
            category="custom_validation",
            tags=["validation", "meli", validation.validation_type.lower()],
            metadata={
                "attribute_name": validation.attribute_name,
                "validation_type": validation.validation_type
            }
        )
    
    def map_category_to_ruleset(self, category: MeliCategory) -> CanonicalRuleSet:
        """
        Map a MELI category with its attributes to a canonical rule set.
        
        Args:
            category: MELI category with attributes
            
        Returns:
            Canonical rule set
        """
        rules = []
        
        # Process attributes if available
        if category.attributes:
            for attribute in category.attributes:
                rules.extend(self.map_attribute_to_rules(attribute))
        
        # Create rule set
        return CanonicalRuleSet(
            marketplace_id=self.marketplace_id,
            name=f"{category.name} Rules",
            version="1.0.0",
            rules=rules,
            metadata={
                "category_id": category.id,
                "category_name": category.name,
                "category_path": category.path_from_root,
                "total_items": category.total_items_in_this_category
            }
        )
    
    def map_meli_ruleset(self, meli_ruleset: MeliRuleSet) -> CanonicalRuleSet:
        """
        Map a complete MELI rule set to canonical format.
        
        Args:
            meli_ruleset: Complete MELI rule set
            
        Returns:
            Canonical rule set
        """
        rules = []
        
        # Process required attributes (create copy to avoid mutation)
        for attribute in meli_ruleset.required_attributes:
            # Create a copy of the attribute with required=True
            attr_copy = attribute.model_copy(update={"required": True})
            rules.extend(self.map_attribute_to_rules(attr_copy))
        
        # Process optional attributes (create copy to avoid mutation)
        for attribute in meli_ruleset.optional_attributes:
            # Create a copy of the attribute with required=False
            attr_copy = attribute.model_copy(update={"required": False})
            rules.extend(self.map_attribute_to_rules(attr_copy))
        
        # Process validation rules
        for validation in meli_ruleset.validation_rules:
            rule = self.map_validation_rule(validation)
            if rule:
                rules.append(rule)
        
        # Create rule set
        return CanonicalRuleSet(
            marketplace_id=self.marketplace_id,
            name=f"MELI Category {meli_ruleset.category_id} Rules",
            version="1.0.0",
            rules=rules,
            metadata={
                "category_id": meli_ruleset.category_id,
                "site_id": meli_ruleset.site_id,
                "category": meli_ruleset.category.model_dump() if meli_ruleset.category else None,
                "listing_types": [lt.model_dump() for lt in meli_ruleset.listing_types],
                "conditions": [c.model_dump() for c in meli_ruleset.conditions],
                "shipping_options": meli_ruleset.shipping_options.model_dump() if meli_ruleset.shipping_options else None
            }
        )
    
    def enrich_with_dependencies(self, ruleset: CanonicalRuleSet) -> CanonicalRuleSet:
        """
        Enrich rule set with dependency information.
        
        This method analyzes rules to identify dependencies between fields.
        
        Args:
            ruleset: Rule set to enrich
            
        Returns:
            Enriched rule set
        """
        # Map field dependencies
        field_deps = {}
        
        for rule in ruleset.rules:
            # Check for conditional dependencies in metadata
            if rule.metadata.get("depends_on"):
                deps = rule.metadata["depends_on"]
                if isinstance(deps, str):
                    deps = [deps]
                rule.depends_on = deps
            
            # Analyze rule conditions
            if rule.condition:
                if rule.condition.field not in rule.depends_on:
                    rule.depends_on.append(rule.condition.field)
        
        return ruleset
