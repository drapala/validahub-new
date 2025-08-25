"""
Main orchestrator for importing MELI rules.
Coordinates the client, mapper, and error translator.
"""

from typing import Optional, Dict, Any, List
import json
import asyncio
from datetime import datetime, timezone
from pathlib import Path

from core.logging_config import get_logger
from core.result import Result, Ok, Err
from ..clients.meli_client import MeliClient
from ..mappers.meli_to_canonical_mapper import MeliToCanonicalMapper
from ..errors.meli_error_translator import MeliErrorTranslator, CanonicalError
from ..models.canonical_rule import CanonicalRuleSet
from ..models.meli_models import (
    MeliRuleSet,
    MeliCategory,
    MeliRuleAttribute,
    MeliItemValidationRule,
    MeliApiError
)

logger = get_logger(__name__)


class MeliRulesImporter:
    """
    Orchestrator for importing MELI marketplace rules.
    
    This class coordinates:
    - Fetching rules from MELI API
    - Transforming to canonical format
    - Handling errors
    - Caching and persistence
    """
    
    def __init__(
        self,
        client: Optional[MeliClient] = None,
        mapper: Optional[MeliToCanonicalMapper] = None,
        error_translator: Optional[MeliErrorTranslator] = None,
        cache_dir: Optional[Path] = None,
        cache_ttl_hours: int = 24
    ):
        """
        Initialize the importer.
        
        Args:
            client: MELI API client
            mapper: Rule mapper
            error_translator: Error translator
            cache_dir: Directory for caching rules
            cache_ttl_hours: Cache time-to-live in hours
        """
        self.client = client
        self.mapper = mapper or MeliToCanonicalMapper()
        self.error_translator = error_translator or MeliErrorTranslator()
        self.cache_dir = Path(cache_dir) if cache_dir else Path("cache/meli_rules")
        self.cache_ttl_hours = cache_ttl_hours
        
        # Create cache directory if needed
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    async def import_category_rules(
        self,
        category_id: str,
        use_cache: bool = True,
        save_cache: bool = True
    ) -> Result[CanonicalRuleSet, List[CanonicalError]]:
        """
        Import rules for a specific MELI category.
        
        Args:
            category_id: MELI category ID
            use_cache: Whether to use cached rules if available
            save_cache: Whether to save fetched rules to cache
            
        Returns:
            Result with CanonicalRuleSet or list of errors
        """
        try:
            # Check cache first
            if use_cache:
                cached_rules = await self._load_from_cache(category_id)
                if cached_rules:
                    logger.info(f"Loaded category {category_id} rules from cache")
                    return Ok(cached_rules)
            
            # Ensure client is available
            if not self.client:
                return Err([
                    self.error_translator.translate_http_error(
                        500, "MELI client not configured"
                    )
                ])
            
            # Fetch from MELI API
            async with self.client:
                # Get category info
                category = await self.client.get_category(category_id)
                if not category:
                    return Err([
                        self.error_translator.translate_http_error(
                            404, f"Category {category_id} not found"
                        )
                    ])
                
                # Get category attributes
                attributes = await self.client.get_category_attributes(category_id)
                
                # Get listing types and conditions
                listing_types = await self.client.get_listing_types()
                conditions = await self.client.get_item_conditions()
                
                # TODO: Fetch validation rules from API when endpoint is available
                # validation_rules = await self.client.get_category_validation_rules(category_id)
                validation_rules = []  # Currently empty, to be implemented
                
                # Build MELI rule set
                meli_ruleset = MeliRuleSet(
                    category_id=category_id,
                    site_id=self.client.site_id,
                    category=category,
                    required_attributes=[
                        attr for attr in attributes if attr.required
                    ],
                    optional_attributes=[
                        attr for attr in attributes if not attr.required
                    ],
                    validation_rules=validation_rules,
                    listing_types=listing_types,
                    conditions=conditions
                )
                
                # Transform to canonical format
                canonical_ruleset = self.mapper.map_meli_ruleset(meli_ruleset)
                canonical_ruleset = self.mapper.enrich_with_dependencies(canonical_ruleset)
                
                # Save to cache if requested
                if save_cache:
                    await self._save_to_cache(category_id, canonical_ruleset)
                
                logger.info(f"Successfully imported {len(canonical_ruleset.rules)} rules for category {category_id}")
                return Ok(canonical_ruleset)
                
        except MeliApiError as e:
            # Handle MELI API specific errors
            logger.error(f"MELI API error importing category {category_id}: {e}")
            return Err([
                self.error_translator.translate_meli_error(e)
            ])
        except (ConnectionError, TimeoutError) as e:
            # Handle network-related errors
            logger.error(f"Network error importing category {category_id}: {e}")
            return Err([
                self.error_translator.translate_http_error(
                    503, f"Service unavailable: {str(e)}"
                )
            ])
        except ValueError as e:
            # Handle data validation errors
            logger.error(f"Data validation error for category {category_id}: {e}")
            return Err([
                self.error_translator.translate_http_error(
                    400, f"Invalid data: {str(e)}"
                )
            ])
        except Exception as e:
            # Only catch truly unexpected errors
            logger.exception(f"Unexpected error importing category {category_id}")
            return Err([
                self.error_translator.translate_http_error(
                    500, f"Internal error during import"
                )
            ])
    
    async def import_multiple_categories(
        self,
        category_ids: List[str],
        use_cache: bool = True,
        save_cache: bool = True,
        max_concurrent: int = 5
    ) -> Dict[str, Result[CanonicalRuleSet, List[CanonicalError]]]:
        """
        Import rules for multiple categories in parallel.
        
        Args:
            category_ids: List of category IDs
            use_cache: Whether to use cached rules
            save_cache: Whether to save fetched rules
            max_concurrent: Maximum number of concurrent imports
            
        Returns:
            Dictionary mapping category_id to Result
        """
        import asyncio
        
        # Validate max_concurrent parameter
        if max_concurrent <= 0:
            raise ValueError(f"max_concurrent must be positive, got {max_concurrent}")
        
        results = {}
        
        # Create tasks for parallel execution
        async def import_with_id(cat_id: str):
            result = await self.import_category_rules(
                cat_id,
                use_cache=use_cache,
                save_cache=save_cache
            )
            return cat_id, result
        
        # Process in batches to limit concurrency
        for i in range(0, len(category_ids), max_concurrent):
            batch = category_ids[i:i + max_concurrent]
            tasks = [import_with_id(cat_id) for cat_id in batch]
            
            # Execute batch in parallel
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results with proper mapping
            for idx, result in enumerate(batch_results):
                cat_id = batch[idx]  # Use index to correctly map category ID
                # Handle both Exception and BaseException (like CancelledError)
                if isinstance(result, BaseException):
                    error_msg = f"Import failed: {str(result)}"
                    if isinstance(result, asyncio.CancelledError):
                        error_msg = "Import cancelled"
                        logger.warning(f"Import cancelled for category {cat_id}")
                    else:
                        logger.error(f"Failed to import category {cat_id}: {result}")
                    
                    # Create error result for exception
                    results[cat_id] = Err([
                        self.error_translator.translate_http_error(
                            500, error_msg
                        )
                    ])
                else:
                    # Result is tuple (cat_id, import_result)
                    _, import_result = result
                    results[cat_id] = import_result
        
        return results
    
    async def search_and_import_category(
        self,
        query: str,
        use_cache: bool = True,
        save_cache: bool = True
    ) -> Result[CanonicalRuleSet, List[CanonicalError]]:
        """
        Search for a category by name and import its rules.
        
        Args:
            query: Search query for category
            use_cache: Whether to use cached rules
            save_cache: Whether to save fetched rules
            
        Returns:
            Result with CanonicalRuleSet or errors
        """
        try:
            if not self.client:
                return Err([
                    self.error_translator.translate_http_error(
                        500, "MELI client not configured"
                    )
                ])
            
            async with self.client:
                # Search for categories
                search_results = await self.client.search_categories(query)
                
                if not search_results:
                    return Err([
                        self.error_translator.translate_http_error(
                            404, f"No categories found for query: {query}"
                        )
                    ])
                
                # Use the first result
                category_id = search_results[0].get("category_id")
                if not category_id:
                    return Err([
                        self.error_translator.translate_http_error(
                            500, "Invalid search result format"
                        )
                    ])
                
                # Import the category rules
                return await self.import_category_rules(
                    category_id,
                    use_cache=use_cache,
                    save_cache=save_cache
                )
                
        except Exception as e:
            logger.error(f"Failed to search and import category: {e}")
            return Err([
                self.error_translator.translate_http_error(
                    500, f"Search and import failed: {str(e)}"
                )
            ])
    
    def validate_data_against_rules(
        self,
        data: Dict[str, Any],
        ruleset: CanonicalRuleSet
    ) -> Dict[str, Any]:
        """
        Validate data against a canonical rule set.
        
        Args:
            data: Data to validate
            ruleset: Canonical rule set
            
        Returns:
            Validation results with errors grouped by field
        """
        errors = ruleset.validate_data(data)
        
        result = {
            "valid": len(errors) == 0,
            "total_errors": sum(len(msgs) for msgs in errors.values()),
            "errors": errors,
            "required_fields": ruleset.get_required_fields(),
            "validated_at": datetime.now(timezone.utc).isoformat()
        }
        
        return result
    
    async def _load_from_cache(self, category_id: str) -> Optional[CanonicalRuleSet]:
        """
        Load rules from cache (async).
        
        Args:
            category_id: Category ID
            
        Returns:
            Cached rule set or None
        """
        cache_file = self.cache_dir / f"{category_id}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            # Check cache age using timezone-aware timestamps
            cache_age_hours = (
                datetime.now(timezone.utc).timestamp() - cache_file.stat().st_mtime
            ) / 3600
            
            if cache_age_hours > self.cache_ttl_hours:
                logger.info(f"Cache for {category_id} is expired ({cache_age_hours:.1f} hours old)")
                return None
            
            # Load from file using asyncio.to_thread to avoid blocking
            data = await asyncio.to_thread(
                self._read_cache_file,
                cache_file
            )
            
            if data:
                return CanonicalRuleSet(**data)
            return None
            
        except Exception as e:
            logger.warning(f"Failed to load cache for {category_id}: {e}")
            return None
    
    def _read_cache_file(self, cache_file: Path) -> Optional[Dict]:
        """Synchronous file read operation for executor."""
        try:
            with open(cache_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse cache file {cache_file}: {e}")
            return None
        except IOError as e:
            logger.error(f"Failed to read cache file {cache_file}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error reading cache file {cache_file}: {e}")
            return None
    
    async def _save_to_cache(self, category_id: str, ruleset: CanonicalRuleSet):
        """
        Save rules to cache (async).
        
        Args:
            category_id: Category ID
            ruleset: Rule set to save
        """
        cache_file = self.cache_dir / f"{category_id}.json"
        
        try:
            # Save to file using asyncio.to_thread to avoid blocking
            await asyncio.to_thread(
                self._write_cache_file,
                cache_file,
                ruleset.model_dump()
            )
            
            logger.info(f"Saved category {category_id} rules to cache")
            
        except Exception as e:
            logger.warning(f"Failed to save cache for {category_id}: {e}")
    
    def _write_cache_file(self, cache_file: Path, data: Dict):
        """Synchronous file write operation for executor."""
        try:
            with open(cache_file, "w") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to write cache file: {e}")
    
    def export_rules_to_file(
        self,
        ruleset: CanonicalRuleSet,
        output_path: Path,
        format: str = "json"
    ) -> Result[Path, str]:
        """
        Export rule set to file.
        
        Args:
            ruleset: Rule set to export
            output_path: Output file path
            format: Export format (json, yaml, csv)
            
        Returns:
            Result with output path or error
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format == "json":
                with open(output_path, "w") as f:
                    json.dump(ruleset.model_dump(), f, indent=2, default=str)
            
            elif format == "yaml":
                import yaml
                with open(output_path, "w") as f:
                    yaml.safe_dump(ruleset.model_dump(), f, default_flow_style=False)
            
            elif format == "csv":
                import csv
                with open(output_path, "w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=[
                        "id", "field_name", "rule_type", "data_type",
                        "severity", "message", "params"
                    ])
                    writer.writeheader()
                    
                    for rule in ruleset.rules:
                        writer.writerow({
                            "id": rule.id,
                            "field_name": rule.field_name,
                            "rule_type": rule.rule_type.value,
                            "data_type": rule.data_type.value,
                            "severity": rule.severity.value,
                            "message": rule.message,
                            "params": json.dumps(rule.params)
                        })
            
            else:
                return Err(f"Unsupported format: {format}")
            
            logger.info(f"Exported rules to {output_path}")
            return Ok(output_path)
            
        except Exception as e:
            logger.error(f"Failed to export rules: {e}")
            return Err(f"Export failed: {str(e)}")
