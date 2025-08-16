"""
Unit tests for refactored rule engine service.
Tests dependency injection and filesystem decoupling.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock
from pathlib import Path

from src.core.interfaces.rule_engine import (
    IRulesetRepository,
    IRuleEngine,
    IRuleEngineFactory
)
from src.services.rule_engine_service_v2 import (
    RuleEngineServiceV2,
    RuleEngineServiceConfig,
    RuleEngineAdapter
)
from src.infrastructure.repositories.ruleset_repository import (
    FileSystemRulesetRepository,
    CachedRulesetRepository
)


class TestRuleEngineServiceV2:
    """Test the refactored rule engine service."""
    
    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository."""
        repo = AsyncMock(spec=IRulesetRepository)
        repo.get_ruleset.return_value = {
            "version": "1.0",
            "name": "Test Rules",
            "rules": [
                {
                    "id": "price_required",
                    "field": "price",
                    "type": "required"
                }
            ],
            "mappings": {}
        }
        return repo
    
    @pytest.fixture
    def mock_engine(self):
        """Create a mock rule engine."""
        engine = Mock(spec=IRuleEngine)
        engine.execute.return_value = []
        return engine
    
    @pytest.fixture
    def mock_factory(self, mock_engine):
        """Create a mock factory that returns the mock engine."""
        factory = Mock(spec=IRuleEngineFactory)
        factory.create_engine.return_value = mock_engine
        return factory
    
    @pytest.fixture
    def service(self, mock_repository, mock_factory):
        """Create service with mocked dependencies."""
        config = RuleEngineServiceConfig(cache_engines=True)
        return RuleEngineServiceV2(
            repository=mock_repository,
            factory=mock_factory,
            config=config
        )
    
    @pytest.mark.asyncio
    async def test_service_uses_repository_not_filesystem(self, service, mock_repository):
        """Test that service uses repository instead of filesystem."""
        # Act
        await service.validate_row({"price": 10}, "test_marketplace", 1)
        
        # Assert - repository was called
        mock_repository.get_ruleset.assert_called_once_with("test_marketplace")
    
    @pytest.mark.asyncio
    async def test_service_caches_engines(self, service, mock_repository, mock_factory):
        """Test that engines are cached after first creation."""
        # Act - call twice with same marketplace
        await service.validate_row({"price": 10}, "test_marketplace", 1)
        await service.validate_row({"price": 20}, "test_marketplace", 2)
        
        # Assert - factory and repository called only once
        mock_factory.create_engine.assert_called_once()
        mock_repository.get_ruleset.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_service_reload_clears_cache(self, service, mock_repository, mock_factory):
        """Test that reload clears cached engine."""
        # Setup - populate cache
        await service.validate_row({"price": 10}, "test_marketplace", 1)
        
        # Act - reload
        await service.reload_marketplace_rules("test_marketplace")
        
        # Call again should create new engine
        await service.validate_row({"price": 20}, "test_marketplace", 2)
        
        # Assert - factory called twice (once before reload, once after)
        assert mock_factory.create_engine.call_count == 2
    
    @pytest.mark.asyncio
    async def test_validate_and_fix_preserves_original(self, service, mock_engine):
        """Test that validate_and_fix doesn't modify original row."""
        # Setup
        original_row = {"price": 10, "title": "Product"}
        mock_engine.execute.return_value = [
            Mock(status="FIXED", fixes=[{"field": "price", "original": 10, "fixed": 15}])
        ]
        
        # Act
        fixed_row, items = await service.validate_and_fix_row(
            original_row, "test_marketplace", 1
        )
        
        # Assert - original unchanged
        assert original_row == {"price": 10, "title": "Product"}
        assert fixed_row != original_row  # Different objects


class TestFileSystemRepository:
    """Test filesystem repository implementation."""
    
    @pytest.fixture
    def temp_rulesets_dir(self, tmp_path):
        """Create temporary directory for rulesets."""
        rulesets_dir = tmp_path / "rulesets"
        rulesets_dir.mkdir()
        
        # Create test ruleset file
        test_ruleset = rulesets_dir / "test_marketplace.yaml"
        test_ruleset.write_text("""
version: "1.0"
name: "Test Marketplace Rules"
rules:
  - id: price_positive
    field: price
    type: range
    min: 0
mappings:
  price: preço
""")
        return rulesets_dir
    
    @pytest.fixture
    def repository(self, temp_rulesets_dir):
        """Create repository with temp directory."""
        return FileSystemRulesetRepository(temp_rulesets_dir)
    
    @pytest.mark.asyncio
    async def test_get_ruleset_from_file(self, repository):
        """Test loading ruleset from YAML file."""
        # Act
        ruleset = await repository.get_ruleset("test_marketplace")
        
        # Assert
        assert ruleset["version"] == "1.0"
        assert ruleset["name"] == "Test Marketplace Rules"
        assert len(ruleset["rules"]) == 1
        assert ruleset["rules"][0]["id"] == "price_positive"
    
    @pytest.mark.asyncio
    async def test_get_ruleset_fallback_to_default(self, repository, temp_rulesets_dir):
        """Test fallback to default.yaml when marketplace not found."""
        # Setup - create default.yaml
        default_ruleset = temp_rulesets_dir / "default.yaml"
        default_ruleset.write_text("""
version: "1.0"
name: "Default Rules"
rules: []
""")
        
        # Act
        ruleset = await repository.get_ruleset("nonexistent")
        
        # Assert - should get default
        assert ruleset["name"] == "Default Rules"
    
    @pytest.mark.asyncio
    async def test_save_ruleset(self, repository, temp_rulesets_dir):
        """Test saving ruleset to file."""
        # Setup
        new_ruleset = {
            "version": "2.0",
            "name": "New Rules",
            "rules": [],
            "mappings": {}
        }
        
        # Act
        await repository.save_ruleset("new_marketplace", new_ruleset)
        
        # Assert - file created
        saved_file = temp_rulesets_dir / "new_marketplace.yaml"
        assert saved_file.exists()
        
        # Verify content
        loaded = await repository.get_ruleset("new_marketplace")
        assert loaded["version"] == "2.0"
        assert loaded["name"] == "New Rules"
    
    @pytest.mark.asyncio
    async def test_list_marketplaces(self, repository, temp_rulesets_dir):
        """Test listing available marketplaces."""
        # Setup - create additional files
        (temp_rulesets_dir / "marketplace1.yaml").write_text("version: 1.0")
        (temp_rulesets_dir / "marketplace2.yaml").write_text("version: 1.0")
        (temp_rulesets_dir / "default.yaml").write_text("version: 1.0")
        
        # Act
        marketplaces = await repository.list_marketplaces()
        
        # Assert - default excluded
        assert "test_marketplace" in marketplaces
        assert "marketplace1" in marketplaces
        assert "marketplace2" in marketplaces
        assert "default" not in marketplaces


class TestCachedRepository:
    """Test caching decorator for repositories."""
    
    @pytest.fixture
    def mock_base_repository(self):
        """Create mock base repository."""
        repo = AsyncMock(spec=IRulesetRepository)
        repo.get_ruleset.return_value = {
            "version": "1.0",
            "name": "Test Rules"
        }
        return repo
    
    @pytest.fixture
    def cached_repository(self, mock_base_repository):
        """Create cached repository with short TTL."""
        return CachedRulesetRepository(
            repository=mock_base_repository,
            cache_ttl=1  # 1 second TTL for testing
        )
    
    @pytest.mark.asyncio
    async def test_cache_hit(self, cached_repository, mock_base_repository):
        """Test that second call uses cache."""
        # Act - call twice
        result1 = await cached_repository.get_ruleset("test")
        result2 = await cached_repository.get_ruleset("test")
        
        # Assert - base repository called only once
        mock_base_repository.get_ruleset.assert_called_once()
        assert result1 == result2
    
    @pytest.mark.asyncio
    async def test_cache_expiry(self, cached_repository, mock_base_repository):
        """Test that cache expires after TTL."""
        # Act
        await cached_repository.get_ruleset("test")
        
        # Wait for cache to expire
        await asyncio.sleep(1.1)
        
        await cached_repository.get_ruleset("test")
        
        # Assert - base repository called twice
        assert mock_base_repository.get_ruleset.call_count == 2
    
    @pytest.mark.asyncio
    async def test_cache_invalidation_on_save(self, cached_repository, mock_base_repository):
        """Test that save invalidates cache."""
        # Setup - populate cache
        await cached_repository.get_ruleset("test")
        
        # Act - save should invalidate
        await cached_repository.save_ruleset("test", {"version": "2.0"})
        
        # Get again should hit base repository
        await cached_repository.get_ruleset("test")
        
        # Assert
        assert mock_base_repository.get_ruleset.call_count == 2
        mock_base_repository.save_ruleset.assert_called_once()