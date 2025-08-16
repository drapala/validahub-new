"""
Configuration settings for the API application.
"""

import os
from typing import Set

class ValidationConfig:
    """Configuration for validation rules and settings."""
    
    # Allowed rulesets for validation (prevents path traversal attacks)
    ALLOWED_RULESETS: Set[str] = {
        "default",
        "strict", 
        "lenient",
        "minimal",
        "comprehensive"
    }
    
    @classmethod
    def get_allowed_rulesets(cls) -> Set[str]:
        """
        Get allowed rulesets from environment or use defaults.
        
        Environment variable format: ALLOWED_RULESETS=default,strict,custom
        """
        env_rulesets = os.getenv("ALLOWED_RULESETS")
        if env_rulesets:
            return set(ruleset.strip() for ruleset in env_rulesets.split(","))
        return cls.ALLOWED_RULESETS
    
    @classmethod
    def is_valid_ruleset(cls, ruleset: str) -> bool:
        """Check if a ruleset is valid."""
        return ruleset in cls.get_allowed_rulesets()