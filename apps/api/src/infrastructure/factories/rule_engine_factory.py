"""
Factory for creating and managing RuleEngine instances.
This separates engine lifecycle management from business logic.
"""

from ..core.logging_config import get_logger
import os
import tempfile
import yaml
from typing import Dict, Optional, List
from dataclasses import dataclass

# TODO: Replace with proper import once libs is properly packaged
import sys
from pathlib import Path
libs_path = Path(__file__).parent.parent.parent.parent.parent.parent / "libs"
if str(libs_path) not in sys.path:
    sys.path.insert(0, str(libs_path))
from rule_engine import RuleEngine

from ..loaders.rule_loader import RuleLoader, RuleLoaderConfig

logger = get_logger(__name__)


@dataclass
class RuleEngineFactoryConfig:
    """Configuration for the rule engine factory."""
    cache_engines: bool = True
    rule_loader_config: Optional[RuleLoaderConfig] = None


class RuleEngineFactory:
    """
    Factory for creating and managing RuleEngine instances.
    
    This class handles:
    - Creating RuleEngine instances
    - Caching engine instances per marketplace
    - Loading rulesets into engines
    - Engine lifecycle management
    """
    
    def __init__(
        self, 
        config: Optional[RuleEngineFactoryConfig] = None,
        rule_loader: Optional[RuleLoader] = None
    ):
        """
        Initialize the factory.
        
        Args:
            config: Factory configuration
            rule_loader: Optional rule loader instance to use
        """
        self.config = config or RuleEngineFactoryConfig()
        self.rule_loader = rule_loader or RuleLoader(self.config.rule_loader_config)
        self._engine_cache: Dict[str, RuleEngine] = {}
        self._ruleset_tempfiles: Dict[str, str] = {}
    
    def __del__(self):
        """Clean up temp files on destruction."""
        try:
            self._cleanup_tempfiles()
        except Exception:
            # Ignore errors during shutdown
            pass
    
    def get_engine(self, marketplace: str) -> RuleEngine:
        """
        Get or create a RuleEngine for the specified marketplace.
        
        Args:
            marketplace: The marketplace identifier
            
        Returns:
            Configured RuleEngine instance
        """
        cache_key = marketplace.lower()
        
        # Check cache
        if self.config.cache_engines and cache_key in self._engine_cache:
            logger.debug(f"Using cached engine for {marketplace}")
            return self._engine_cache[cache_key]
        
        # Create new engine
        engine = self._create_engine(marketplace)
        
        # Cache if configured
        if self.config.cache_engines:
            self._engine_cache[cache_key] = engine
        
        return engine
    
    def _create_engine(self, marketplace: str) -> RuleEngine:
        """
        Create a new RuleEngine instance for the marketplace.
        
        Args:
            marketplace: The marketplace identifier
            
        Returns:
            Configured RuleEngine instance
        """
        logger.info(f"Creating new rule engine for {marketplace}")
        
        # Create engine
        engine = RuleEngine()
        
        # Load ruleset
        ruleset = self.rule_loader.load_ruleset(marketplace)
        
        # Configure engine with ruleset
        if ruleset and ruleset.get('rules'):
            # The RuleEngine.load_ruleset expects a file path,
            # but we already have the loaded dict.
            # Configure engine with cached temp file
            self._configure_engine(engine, ruleset, marketplace)
        else:
            logger.warning(f"No rules found for {marketplace}, using empty engine")
        
        return engine
    
    def _configure_engine(self, engine: RuleEngine, ruleset: dict, marketplace: Optional[str] = None):
        """
        Configure a RuleEngine with a loaded ruleset.
        
        Args:
            engine: The RuleEngine instance to configure
            ruleset: The loaded ruleset dictionary
            marketplace: The marketplace identifier (for temp file caching)
        """
        # Since RuleEngine.load_ruleset expects a file path,
        # we cache temp files to avoid recreating them
        
        # Use marketplace as cache key if provided
        cache_key = marketplace or str(id(ruleset))
        tmp_path = self._ruleset_tempfiles.get(cache_key)
        
        if not tmp_path or not os.path.exists(tmp_path):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp:
                yaml.dump(ruleset, tmp)
                tmp_path = tmp.name
            self._ruleset_tempfiles[cache_key] = tmp_path
        
        engine.load_ruleset(tmp_path)
    
    def clear_cache(self):
        """Clear all cached engines and clean up temp files."""
        self._engine_cache.clear()
        self.rule_loader.clear_cache()
        self._cleanup_tempfiles()
        logger.info("Rule engine factory cache cleared")
    
    def _cleanup_tempfiles(self):
        """Clean up cached temporary ruleset files."""
        for tmp_path in self._ruleset_tempfiles.values():
            try:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            except Exception as e:
                logger.warning(f"Failed to clean up temp file {tmp_path}: {e}")
        self._ruleset_tempfiles.clear()
    
    def reload_engine(self, marketplace: str) -> RuleEngine:
        """
        Reload the engine for a specific marketplace.
        
        Args:
            marketplace: The marketplace identifier
            
        Returns:
            Reloaded RuleEngine instance
        """
        cache_key = marketplace.lower()
        
        # Remove from cache
        self._engine_cache.pop(cache_key, None)
        
        # Reload ruleset
        self.rule_loader.reload_ruleset(marketplace)
        
        # Create new engine
        return self.get_engine(marketplace)
    
    def list_cached_engines(self) -> List[str]:
        """
        List all currently cached engine marketplaces.
        
        Returns:
            List of marketplace names with cached engines
        """
        return sorted(self._engine_cache.keys())
    
    def get_engine_stats(self) -> dict:
        """
        Get statistics about cached engines.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            "cached_engines": len(self._engine_cache),
            "marketplaces": self.list_cached_engines(),
            "available_marketplaces": self.rule_loader.list_available_marketplaces()
        }