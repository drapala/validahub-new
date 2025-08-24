"""
Rule loader component responsible for loading ruleset files.
This separates file system concerns from the business logic.
"""

from ..core.logging_config import get_logger
import yaml
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass

# TODO: Replace with proper import once libs is properly packaged
import sys
libs_path = Path(__file__).parent.parent.parent.parent.parent.parent / "libs"
if str(libs_path) not in sys.path:
    sys.path.insert(0, str(libs_path))
from rule_engine import load_ruleset

logger = get_logger(__name__)


@dataclass
class RuleLoaderConfig:
    """Configuration for rule loader."""
    rulesets_path: Path = None
    fallback_to_default: bool = True
    
    def __post_init__(self):
        if self.rulesets_path is None:
            # Default path to rulesets
            self.rulesets_path = Path(__file__).parent.parent.parent.parent.parent.parent / "rulesets"


class RuleLoader:
    """
    Responsible for loading ruleset files from the filesystem.
    
    This class handles:
    - Finding ruleset files by marketplace
    - Loading YAML ruleset files
    - Fallback to default ruleset
    - Caching loaded rulesets
    """
    
    def __init__(self, config: Optional[RuleLoaderConfig] = None):
        """Initialize rule loader with configuration."""
        self.config = config or RuleLoaderConfig()
        self._cache: Dict[str, dict] = {}
    
    def load_ruleset(self, marketplace: str, use_cache: bool = True) -> dict:
        """
        Load ruleset for a specific marketplace.
        
        Args:
            marketplace: The marketplace identifier
            use_cache: Whether to use cached rulesets
            
        Returns:
            Dict containing the ruleset configuration
        """
        cache_key = marketplace.lower()
        
        # Check cache
        if use_cache and cache_key in self._cache:
            logger.debug(f"Using cached ruleset for {marketplace}")
            return self._cache[cache_key]
        
        # Load from filesystem
        ruleset = self._load_from_file(marketplace)
        
        # Cache the result
        if use_cache:
            self._cache[cache_key] = ruleset
        
        return ruleset
    
    def _load_from_file(self, marketplace: str) -> dict:
        """
        Load ruleset from YAML file.
        
        Args:
            marketplace: The marketplace identifier
            
        Returns:
            Dict containing the ruleset configuration
        """
        ruleset_file = self._find_ruleset_file(marketplace)
        
        if not ruleset_file.exists():
            logger.error(f"No ruleset file found for {marketplace}")
            return self._get_empty_ruleset(marketplace)
        
        try:
            logger.info(f"Loading ruleset from {ruleset_file}")
            # Load YAML file directly
            with open(ruleset_file, 'r') as f:
                ruleset = yaml.safe_load(f)
            return ruleset
        except Exception as e:
            logger.error(f"Error loading ruleset for {marketplace}: {e}")
            return self._get_empty_ruleset(marketplace)
    
    def _find_ruleset_file(self, marketplace: str) -> Path:
        """
        Find the ruleset file for a marketplace.
        
        Args:
            marketplace: The marketplace identifier
            
        Returns:
            Path to the ruleset file
        """
        # Try marketplace-specific ruleset
        ruleset_file = self.config.rulesets_path / f"{marketplace.lower()}.yaml"
        
        # Fallback to default if configured and not found
        if not ruleset_file.exists() and self.config.fallback_to_default:
            logger.warning(f"Ruleset not found for {marketplace}, using default")
            ruleset_file = self.config.rulesets_path / "default.yaml"
        
        return ruleset_file
    
    def _get_empty_ruleset(self, marketplace: str) -> dict:
        """
        Get an empty ruleset structure.
        
        Args:
            marketplace: The marketplace identifier
            
        Returns:
            Dict with minimal ruleset structure
        """
        return {
            "version": "1.0",
            "name": f"{marketplace} Rules",
            "rules": [],
            "mappings": {}
        }
    
    def clear_cache(self):
        """Clear all cached rulesets."""
        self._cache.clear()
        logger.info("Rule loader cache cleared")
    
    def reload_ruleset(self, marketplace: str) -> dict:
        """
        Reload a specific marketplace ruleset from file.
        
        Args:
            marketplace: The marketplace identifier
            
        Returns:
            Dict containing the reloaded ruleset
        """
        cache_key = marketplace.lower()
        
        # Remove from cache
        self._cache.pop(cache_key, None)
        
        # Reload from file
        return self.load_ruleset(marketplace, use_cache=True)
    
    def list_available_marketplaces(self) -> List[str]:
        """
        List all available marketplace rulesets.
        
        Returns:
            List of marketplace names with available rulesets
        """
        if not self.config.rulesets_path.exists():
            return []
        
        marketplaces = []
        for yaml_file in self.config.rulesets_path.glob("*.yaml"):
            if yaml_file.stem != "default":
                marketplaces.append(yaml_file.stem)
        
        return sorted(marketplaces)