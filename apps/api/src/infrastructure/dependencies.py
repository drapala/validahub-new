"""
Dependency injection configuration.
Sets up repositories, services, and factories based on environment.
"""

import os
import logging
from pathlib import Path
from typing import Optional

from ..core.interfaces.rule_engine import (
    IRulesetRepository,
    IRuleEngineFactory,
    IRuleEngineService
)
from .repositories.ruleset_repository import (
    FileSystemRulesetRepository,
    S3RulesetRepository,
    DatabaseRulesetRepository,
    CachedRulesetRepository
)
from ..services.rule_engine_service_v2 import (
    RuleEngineServiceV2,
    RuleEngineFactory,
    RuleEngineServiceConfig
)

logger = logging.getLogger(__name__)


def get_ruleset_repository() -> IRulesetRepository:
    """
    Factory function to get the appropriate ruleset repository.
    Based on environment configuration.
    """
    storage_type = os.environ.get("RULESET_STORAGE", "filesystem").lower()
    cache_enabled = os.environ.get("RULESET_CACHE_ENABLED", "true").lower() == "true"
    cache_ttl = int(os.environ.get("RULESET_CACHE_TTL", "3600"))
    
    repository: IRulesetRepository
    
    if storage_type == "filesystem":
        rulesets_path = Path(os.environ.get(
            "RULESETS_PATH",
            str(Path(__file__).parent.parent.parent.parent.parent / "rulesets")
        ))
        repository = FileSystemRulesetRepository(rulesets_path)
        logger.info(f"Using filesystem repository at {rulesets_path}")
        
    elif storage_type == "s3":
        bucket_name = os.environ.get("RULESET_S3_BUCKET", "validahub-rulesets")
        prefix = os.environ.get("RULESET_S3_PREFIX", "rulesets/")
        repository = S3RulesetRepository(bucket_name, prefix)
        logger.info(f"Using S3 repository with bucket {bucket_name}")
        
    elif storage_type == "database":
        # Get database session from environment or configuration
        # Note: This requires proper database configuration
        try:
            from ..database import get_db_session  # Assuming you have a database module
            db_session = get_db_session()
            repository = DatabaseRulesetRepository(db_session)
            logger.info("Using database repository with configured session")
        except ImportError:
            logger.warning("Database module not found. Using None for db_session.")
            logger.warning("Please implement get_db_session() in your database module.")
            repository = DatabaseRulesetRepository(None)
            logger.info("Using database repository (session not configured)")
        
    else:
        raise ValueError(f"Unknown storage type: {storage_type}")
    
    # Add caching if enabled
    if cache_enabled:
        repository = CachedRulesetRepository(repository, cache_ttl)
        logger.info(f"Caching enabled with TTL {cache_ttl}s")
    
    return repository


def get_rule_engine_factory() -> IRuleEngineFactory:
    """
    Get the rule engine factory.
    """
    return RuleEngineFactory()


def get_rule_engine_service() -> IRuleEngineService:
    """
    Get the configured rule engine service.
    Uses dependency injection to provide the service.
    """
    repository = get_ruleset_repository()
    factory = get_rule_engine_factory()
    
    config = RuleEngineServiceConfig(
        cache_engines=os.environ.get("ENGINE_CACHE_ENABLED", "true").lower() == "true",
        max_cached_engines=int(os.environ.get("MAX_CACHED_ENGINES", "10"))
    )
    
    return RuleEngineServiceV2(
        repository=repository,
        factory=factory,
        config=config
    )


# Singleton instances (optional, for performance)
_rule_engine_service: Optional[IRuleEngineService] = None


def get_rule_engine_service_singleton() -> IRuleEngineService:
    """
    Get singleton instance of rule engine service.
    Useful for avoiding recreation on every request.
    """
    global _rule_engine_service
    
    if _rule_engine_service is None:
        _rule_engine_service = get_rule_engine_service()
    
    return _rule_engine_service