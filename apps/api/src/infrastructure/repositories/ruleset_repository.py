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
        self._client = None
        logger.info(f"S3 repository initialized with bucket: {bucket_name}")
    
    def _get_client(self):
        """Lazy initialization of boto3 client."""
        if self._client is None:
            try:
                import boto3
                self._client = boto3.client('s3')
            except ImportError:
                logger.error("boto3 not installed. Install with: pip install boto3")
                raise ImportError("boto3 is required for S3 storage")
        return self._client
    
    async def get_ruleset(self, marketplace: str) -> Dict[str, Any]:
        """
        Load ruleset from S3.
        
        Args:
            marketplace: The marketplace identifier
            
        Returns:
            Dict containing ruleset configuration
        """
        import asyncio
        
        key = f"{self.prefix}{marketplace.lower()}.yaml"
        
        try:
            client = self._get_client()
            loop = asyncio.get_event_loop()
            
            # Run boto3 call in executor since it's not async
            response = await loop.run_in_executor(
                None,
                client.get_object,
                self.bucket_name,
                key
            )
            
            content = response['Body'].read().decode('utf-8')
            ruleset = yaml.safe_load(content)
            return ruleset or self._empty_ruleset(marketplace)
            
        except client.exceptions.NoSuchKey:
            logger.warning(f"No ruleset found for {marketplace} in S3")
            return self._empty_ruleset(marketplace)
        except Exception as e:
            logger.error(f"Error loading ruleset from S3 for {marketplace}: {e}")
            return self._empty_ruleset(marketplace)
    
    async def save_ruleset(self, marketplace: str, ruleset: Dict[str, Any]) -> None:
        """
        Save ruleset to S3.
        
        Args:
            marketplace: The marketplace identifier
            ruleset: The ruleset configuration to save
        """
        import asyncio
        
        key = f"{self.prefix}{marketplace.lower()}.yaml"
        content = yaml.dump(ruleset, default_flow_style=False, sort_keys=False)
        
        try:
            client = self._get_client()
            loop = asyncio.get_event_loop()
            
            await loop.run_in_executor(
                None,
                client.put_object,
                Bucket=self.bucket_name,
                Key=key,
                Body=content.encode('utf-8'),
                ContentType='application/x-yaml'
            )
            
            logger.info(f"Saved ruleset for {marketplace} to S3")
        except Exception as e:
            logger.error(f"Error saving ruleset to S3 for {marketplace}: {e}")
            raise
    
    async def list_marketplaces(self) -> List[str]:
        """
        List all marketplaces in S3.
        
        Returns:
            List of marketplace identifiers
        """
        import asyncio
        
        try:
            client = self._get_client()
            loop = asyncio.get_event_loop()
            
            response = await loop.run_in_executor(
                None,
                client.list_objects_v2,
                self.bucket_name,
                self.prefix
            )
            
            marketplaces = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    key = obj['Key']
                    if key.startswith(self.prefix) and key.endswith('.yaml'):
                        marketplace = key[len(self.prefix):-5]  # Remove prefix and .yaml
                        marketplaces.append(marketplace)
            
            return marketplaces
        except Exception as e:
            logger.error(f"Error listing marketplaces from S3: {e}")
            return []
    
    async def exists(self, marketplace: str) -> bool:
        """
        Check if ruleset exists in S3.
        
        Args:
            marketplace: The marketplace identifier
            
        Returns:
            True if ruleset exists, False otherwise
        """
        import asyncio
        
        key = f"{self.prefix}{marketplace.lower()}.yaml"
        
        try:
            client = self._get_client()
            loop = asyncio.get_event_loop()
            
            await loop.run_in_executor(
                None,
                client.head_object,
                self.bucket_name,
                key
            )
            return True
        except client.exceptions.ClientError:
            return False
        except Exception as e:
            logger.error(f"Error checking existence in S3 for {marketplace}: {e}")
            return False
    
    def _empty_ruleset(self, marketplace: str) -> Dict[str, Any]:
        """Return empty ruleset structure."""
        return {
            "version": "1.0",
            "name": f"{marketplace} Rules",
            "rules": [],
            "mappings": {}
        }


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
    
    def _get_session(self):
        """Get database session."""
        if self.db_session is None:
            raise RuntimeError("Database session not configured. Please provide a valid session.")
    
    async def get_ruleset(self, marketplace: str) -> Dict[str, Any]:
        """
        Load ruleset from database.
        
        Args:
            marketplace: The marketplace identifier
            
        Returns:
            Dict containing ruleset configuration
        """
        # Note: This is a placeholder implementation
        # The actual implementation would depend on your ORM and database schema
        logger.warning(f"Database loading for {marketplace} - implementation pending database schema")
        
        # Example implementation with SQLAlchemy (commented out):
        # try:
        #     async with self.db_session() as session:
        #         from sqlalchemy import select
        #         from ..models import Ruleset  # Assuming you have a Ruleset model
        #         
        #         stmt = select(Ruleset).where(Ruleset.marketplace == marketplace.lower())
        #         result = await session.execute(stmt)
        #         ruleset_obj = result.scalar_one_or_none()
        #         
        #         if ruleset_obj is None:
        #             logger.warning(f"No ruleset found for {marketplace} in database")
        #             return self._empty_ruleset(marketplace)
        #         
        #         return json.loads(ruleset_obj.data) if isinstance(ruleset_obj.data, str) else ruleset_obj.data
        # except Exception as e:
        #     logger.error(f"Error loading ruleset from database for {marketplace}: {e}")
        #     return self._empty_ruleset(marketplace)
        
        return self._empty_ruleset(marketplace)
    
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