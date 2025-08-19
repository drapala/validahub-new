"""
Service layer for integrating the YAML-based rule engine with the API.

This module now imports from the adapter which provides backward compatibility
while using the refactored implementation internally.
"""

# Re-export from adapter for backward compatibility
from .rule_engine_service_adapter import (
    RuleEngineService,
    RuleEngineConfig
)

__all__ = ['RuleEngineService', 'RuleEngineConfig']