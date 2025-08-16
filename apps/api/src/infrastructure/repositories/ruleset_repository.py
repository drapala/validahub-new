"""
Concrete implementations of IRulesetRepository.
Infrastructure layer - knows about filesystem, S3, database, etc.
"""

import json
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import aiofiles
import asyncio

from ...core.interfaces.rule_engine import IRulesetRepository

logger = logging.getLogger(__name__)


class FileSystemRulesetRepository(IRulesetRepository):
    """
    Filesystem-based implementation of ruleset repository.
    Reads YAML files from a directory.
    """
    
    def __init__(self, rulesets_path: Path):
        """
        Initialize filesystem repository.
        
        Args:
            rulesets_path: Path to directory containing ruleset YAML files
        """
        self.rulesets_path = rulesets_path
        if not self.rulesets_path.exists():
            logger.warning(f"Rulesets path does not exist: {rulesets_path}")
            self.rulesets_path.mkdir(parents=True, exist_ok=True)
    
    async def get_ruleset(self, marketplace: str) -> Dict[str, Any]:
        """
        Load ruleset from YAML file.
        
        Args:
            marketplace: The marketplace identifier
            
        Returns:
            Dict containing ruleset configuration
        """
        ruleset_file = self._get_ruleset_file(marketplace)
        
        if not ruleset_file.exists():
            # Try default ruleset
            ruleset_file = self.rulesets_path / "default.yaml"
            if not ruleset_file.exists():
                logger.error(f"No ruleset found for {marketplace} or default")
                return self._empty_ruleset(marketplace)
        
        try:
            async with aiofiles.open(ruleset_file, 'r') as f:
                content = await f.read()
                ruleset = yaml.safe_load(content)
                return ruleset or self._empty_ruleset(marketplace)
        except Exception as e:
            logger.error(f"Error loading ruleset for {marketplace}: {e}")
            return self._empty_ruleset(marketplace)
    
    async def save_ruleset(self, marketplace: str, ruleset: Dict[str, Any]) -> None:
        """
        Save ruleset to YAML file.
        
        Args:
            marketplace: The marketplace identifier
            ruleset: The ruleset configuration to save
        """
        ruleset_file = self._get_ruleset_file(marketplace)
        
        try:
            async with aiofiles.open(ruleset_file, 'w') as f:
                content = yaml.dump(ruleset, default_flow_style=False, sort_keys=False)
                await f.write(content)
            logger.info(f"Saved ruleset for {marketplace} to {ruleset_file}")
        except Exception as e:
            logger.error(f"Error saving ruleset for {marketplace}: {e}")
            raise
    
    async def list_marketplaces(self) -> List[str]:
        """
        List all marketplaces with YAML files.
        
        Returns:
            List of marketplace identifiers
        """
        marketplaces = []
        
        if self.rulesets_path.exists():
            for file in self.rulesets_path.glob("*.yaml"):
                if file.stem != "default":
                    marketplaces.append(file.stem)
        
        return marketplaces
    
    async def exists(self, marketplace: str) -> bool:
        """
        Check if a ruleset file exists.
        
        Args:
            marketplace: The marketplace identifier
            
        Returns:
            True if ruleset exists, False otherwise
        """
        ruleset_file = self._get_ruleset_file(marketplace)
        return ruleset_file.exists()
    
    def _get_ruleset_file(self, marketplace: str) -> Path:
        """Get path to ruleset file for marketplace."""
        return self.rulesets_path / f"{marketplace.lower()}.yaml"
    
    def _empty_ruleset(self, marketplace: str) -> Dict[str, Any]:
        """Return empty ruleset structure."""
        return {
            "version": "1.0",
            "name": f"{marketplace} Rules",
            "rules": [],
            "mappings": {}
        }


class S3RulesetRepository(IRulesetRepository):
    """
    S3-based implementation of ruleset repository.
    Stores rulesets in AWS S3.
    """
    
    def __init__(self, bucket_name: str, prefix: str = "rulesets/"):
        """
        Initialize S3 repository.
        
        Args:
            bucket_name: S3 bucket name
            prefix: Prefix for ruleset objects in bucket
        """
        self.bucket_name = bucket_name
        self.prefix = prefix
        # TODO: Initialize boto3 client
        logger.info(f"S3 repository initialized with bucket: {bucket_name}")
    
    async def get_ruleset(self, marketplace: str) -> Dict[str, Any]:
        """
        Load ruleset from S3.
        
        Args:
            marketplace: The marketplace identifier
            
        Returns:
            Dict containing ruleset configuration
        """
        # TODO: Implement S3 loading
        logger.warning("S3 repository not fully implemented")
        return {
            "version": "1.0",
            "name": f"{marketplace} Rules",
            "rules": [],
            "mappings": {}
        }
    
    async def save_ruleset(self, marketplace: str, ruleset: Dict[str, Any]) -> None:
        """
        Save ruleset to S3.
        
        Args:
            marketplace: The marketplace identifier
            ruleset: The ruleset configuration to save
        """
        # TODO: Implement S3 saving
        logger.warning("S3 save not implemented")
    
    async def list_marketplaces(self) -> List[str]:
        """
        List all marketplaces in S3.
        
        Returns:
            List of marketplace identifiers
        """
        # TODO: Implement S3 listing
        return []
    
    async def exists(self, marketplace: str) -> bool:
        """
        Check if ruleset exists in S3.
        
        Args:
            marketplace: The marketplace identifier
            
        Returns:
            True if ruleset exists, False otherwise
        """
        # TODO: Implement S3 existence check
        return False


class DatabaseRulesetRepository(IRulesetRepository):
    """
    Database-based implementation of ruleset repository.
    Stores rulesets in a database.
    """
    
    def __init__(self, db_session):
        """
        Initialize database repository.
        
        Args:
            db_session: Database session or connection pool
        """
        self.db_session = db_session
        logger.info("Database repository initialized")
    
    async def get_ruleset(self, marketplace: str) -> Dict[str, Any]:
        """
        Load ruleset from database.
        
        Args:
            marketplace: The marketplace identifier
            
        Returns:
            Dict containing ruleset configuration
        """
        # TODO: Implement database loading
        logger.warning("Database repository not fully implemented")
        return {
            "version": "1.0",
            "name": f"{marketplace} Rules",
            "rules": [],
            "mappings": {}
        }
    
    async def save_ruleset(self, marketplace: str, ruleset: Dict[str, Any]) -> None:
        """
        Save ruleset to database.
        
        Args:
            marketplace: The marketplace identifier
            ruleset: The ruleset configuration to save
        """
        # TODO: Implement database saving
        logger.warning("Database save not implemented")
    
    async def list_marketplaces(self) -> List[str]:
        """
        List all marketplaces in database.
        
        Returns:
            List of marketplace identifiers
        """
        # TODO: Implement database listing
        return []
    
    async def exists(self, marketplace: str) -> bool:
        """
        Check if ruleset exists in database.
        
        Args:
            marketplace: The marketplace identifier
            
        Returns:
            True if ruleset exists, False otherwise
        """
        # TODO: Implement database existence check
        return False


class CachedRulesetRepository(IRulesetRepository):
    """
    Caching decorator for any ruleset repository.
    Adds in-memory caching to reduce I/O operations.
    """
    
    def __init__(self, repository: IRulesetRepository, cache_ttl: int = 3600):
        """
        Initialize cached repository.
        
        Args:
            repository: The underlying repository to cache
            cache_ttl: Cache time-to-live in seconds
        """
        self.repository = repository
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamps: Dict[str, float] = {}
    
    async def get_ruleset(self, marketplace: str) -> Dict[str, Any]:
        """
        Get ruleset with caching.
        
        Args:
            marketplace: The marketplace identifier
            
        Returns:
            Dict containing ruleset configuration
        """
        import time
        
        cache_key = marketplace.lower()
        now = time.time()
        
        # Check cache
        if cache_key in self._cache:
            if now - self._cache_timestamps.get(cache_key, 0) < self.cache_ttl:
                logger.debug(f"Cache hit for {marketplace}")
                return self._cache[cache_key]
        
        # Load from underlying repository
        ruleset = await self.repository.get_ruleset(marketplace)
        
        # Update cache
        self._cache[cache_key] = ruleset
        self._cache_timestamps[cache_key] = now
        
        return ruleset
    
    async def save_ruleset(self, marketplace: str, ruleset: Dict[str, Any]) -> None:
        """
        Save ruleset and invalidate cache.
        
        Args:
            marketplace: The marketplace identifier
            ruleset: The ruleset configuration to save
        """
        await self.repository.save_ruleset(marketplace, ruleset)
        
        # Invalidate cache
        cache_key = marketplace.lower()
        if cache_key in self._cache:
            del self._cache[cache_key]
            del self._cache_timestamps[cache_key]
    
    async def list_marketplaces(self) -> List[str]:
        """List marketplaces from underlying repository."""
        return await self.repository.list_marketplaces()
    
    async def exists(self, marketplace: str) -> bool:
        """Check existence in underlying repository."""
        return await self.repository.exists(marketplace)
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
        self._cache_timestamps.clear()
        logger.info("Cache cleared")