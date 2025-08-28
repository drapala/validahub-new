"""
Policy Loader Service - Loads and caches validation policies from YAML files.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from functools import lru_cache
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class PolicyLoader:
    """Loads marketplace policies from YAML files."""
    
    def __init__(self, policies_dir: Optional[Path] = None):
        """Initialize with policies directory."""
        if policies_dir is None:
            # Default to policies directory relative to project root
            self.policies_dir = Path(__file__).parent.parent.parent / "policies"
        else:
            self.policies_dir = Path(policies_dir)
        
        self._cache: Dict[str, Dict[str, Any]] = {}
        logger.info(f"PolicyLoader initialized with directory: {self.policies_dir}")
    
    @lru_cache(maxsize=128)
    def get_policy(
        self, 
        marketplace: str, 
        category: str,
        version: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Load a policy for a specific marketplace and category.
        
        Args:
            marketplace: Marketplace code (MLB, AMZN_BR, etc.)
            category: Category ID (MLB1743, etc.)
            version: Optional specific version (defaults to latest)
            
        Returns:
            Policy dictionary with rules and metadata
        """
        cache_key = f"{marketplace}:{category}:{version or 'latest'}"
        
        # Check cache first
        if cache_key in self._cache:
            logger.debug(f"Policy cache hit: {cache_key}")
            return self._cache[cache_key]
        
        # Build file path
        policy_file = self.policies_dir / marketplace / "categories" / f"{category}.yml"
        
        if not policy_file.exists():
            logger.warning(f"Policy file not found: {policy_file}")
            # Return minimal default policy
            return self._get_default_policy(marketplace, category)
        
        try:
            # Load YAML
            with open(policy_file) as f:
                policy = yaml.safe_load(f)
            
            # Convert datetime objects to strings for consistency
            if isinstance(policy.get("effective_date"), datetime):
                policy["effective_date"] = policy["effective_date"].isoformat()
            if isinstance(policy.get("deprecated_after"), datetime):
                policy["deprecated_after"] = policy["deprecated_after"].isoformat()
            if "source" in policy and isinstance(policy["source"].get("last_fetched"), datetime):
                policy["source"]["last_fetched"] = policy["source"]["last_fetched"].isoformat()
            
            # Validate version if specified
            if version and policy.get("version") != version:
                logger.warning(f"Version mismatch: requested {version}, found {policy.get('version')}")
            
            # Cache the policy
            self._cache[cache_key] = policy
            logger.info(f"Loaded policy: {marketplace}/{category} v{policy.get('version')}")
            
            return policy
            
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML policy: {e}")
            return self._get_default_policy(marketplace, category)
        except Exception as e:
            logger.error(f"Failed to load policy: {e}")
            return self._get_default_policy(marketplace, category)
    
    def _get_default_policy(self, marketplace: str, category: str) -> Dict[str, Any]:
        """
        Return a minimal default policy when specific one is not found.
        This ensures the system continues to work with basic validations.
        """
        logger.warning(f"Using default policy for {marketplace}/{category}")
        
        return {
            "version": "default",
            "marketplace": marketplace,
            "category_id": category,
            "category_name": "Unknown Category",
            "effective_date": datetime.now(timezone.utc).isoformat(),
            "rules": {
                "title": {
                    "required": True,
                    "min_length": 10,
                    "max_length": 60
                },
                "price": {
                    "required": True,
                    "min_value": 0.01,
                    "max_value": 999999.99
                },
                "stock": {
                    "required": True,
                    "min_value": 0,
                    "max_value": 99999
                },
                "brand": {
                    "required": True
                },
                "condition": {
                    "required": True,
                    "enum_values": ["new", "used", "refurbished"]
                }
            },
            "error_codes": {
                "DEFAULT_TITLE_REQUIRED": "Title is required",
                "DEFAULT_PRICE_INVALID": "Price must be positive",
                "DEFAULT_STOCK_INVALID": "Stock must be non-negative"
            }
        }
    
    def list_available_policies(self, marketplace: Optional[str] = None) -> Dict[str, list]:
        """
        List all available policies.
        
        Args:
            marketplace: Optional filter by marketplace
            
        Returns:
            Dictionary with marketplace -> list of categories
        """
        result = {}
        
        if marketplace:
            marketplaces = [marketplace]
        else:
            # Find all marketplace directories
            marketplaces = [d.name for d in self.policies_dir.iterdir() if d.is_dir()]
        
        for mp in marketplaces:
            categories_dir = self.policies_dir / mp / "categories"
            if categories_dir.exists():
                categories = [
                    f.stem for f in categories_dir.glob("*.yml")
                ]
                if categories:
                    result[mp] = categories
        
        return result
    
    def reload_policies(self):
        """Clear cache to force reload of policies."""
        self._cache.clear()
        self.get_policy.cache_clear()
        logger.info("Policy cache cleared")
    
    def validate_policy_structure(self, policy: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate that a policy has the required structure.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required top-level fields
        required_fields = ["version", "marketplace", "category_id", "rules"]
        for field in required_fields:
            if field not in policy:
                errors.append(f"Missing required field: {field}")
        
        # Check rules structure
        if "rules" in policy:
            rules = policy["rules"]
            
            # Check for basic rule fields
            for field_name, rule in rules.items():
                if not isinstance(rule, dict):
                    errors.append(f"Rule '{field_name}' must be a dictionary")
                    continue
                
                # Check min/max consistency
                if "min_length" in rule and "max_length" in rule:
                    if rule["min_length"] > rule["max_length"]:
                        errors.append(f"Rule '{field_name}': min_length > max_length")
                
                if "min_value" in rule and "max_value" in rule:
                    if rule["min_value"] > rule["max_value"]:
                        errors.append(f"Rule '{field_name}': min_value > max_value")
        
        return len(errors) == 0, errors