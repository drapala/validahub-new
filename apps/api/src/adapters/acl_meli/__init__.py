"""
MELI ACL (Anti-Corruption Layer) Module.

This module provides an abstraction layer for integrating with Mercado Livre APIs,
transforming their specific formats into canonical models.
"""

# Bootstrap validation registry with built-in validators
from .models.canonical_rule import DataType
from core.validation.validators_builtin import register_builtin_validators

# Register standard validators for DataTypes
register_builtin_validators(DataType)

# Export main components
from .clients.meli_client import MeliClient
from .mappers.meli_to_canonical_mapper import MeliToCanonicalMapper
from .errors.meli_error_translator import MeliErrorTranslator
from .importers.meli_rules_importer import MeliRulesImporter
from .models.canonical_rule import CanonicalRule, CanonicalRuleSet

__all__ = [
    'MeliClient',
    'MeliToCanonicalMapper',
    'MeliErrorTranslator',
    'MeliRulesImporter',
    'CanonicalRule',
    'CanonicalRuleSet',
    'DataType',
]