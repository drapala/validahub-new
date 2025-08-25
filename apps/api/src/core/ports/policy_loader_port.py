"""Policy loader port for validation policies."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class ValidationPolicy:
    """Validation policy definition."""
    
    id: str
    name: str
    version: str
    rules: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    schema_version: Optional[str] = None


class PolicyLoaderPort(ABC):
    """
    Port for loading and managing validation policies.
    Abstracts policy storage (YAML files, database, API, etc).
    """
    
    @abstractmethod
    async def load_policy(self, policy_id: str) -> ValidationPolicy:
        """
        Load a specific validation policy.
        
        Args:
            policy_id: Policy identifier
            
        Returns:
            ValidationPolicy instance
            
        Raises:
            PolicyNotFoundError: If policy doesn't exist
        """
        pass
    
    @abstractmethod
    async def list_policies(
        self,
        active_only: bool = True,
        marketplace: Optional[str] = None
    ) -> List[ValidationPolicy]:
        """
        List available policies.
        
        Args:
            active_only: Filter only active policies
            marketplace: Filter by marketplace
            
        Returns:
            List of validation policies
        """
        pass
    
    @abstractmethod
    async def save_policy(self, policy: ValidationPolicy) -> bool:
        """
        Save or update a validation policy.
        
        Args:
            policy: Policy to save
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def validate_policy(self, policy: ValidationPolicy) -> List[str]:
        """
        Validate policy structure and rules.
        
        Args:
            policy: Policy to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        pass
    
    @abstractmethod
    async def reload_policies(self) -> int:
        """
        Reload all policies from source.
        
        Returns:
            Number of policies loaded
        """
        pass
    
    @abstractmethod
    async def get_policy_version(self, policy_id: str, version: str) -> ValidationPolicy:
        """
        Get specific version of a policy.
        
        Args:
            policy_id: Policy identifier
            version: Version string
            
        Returns:
            ValidationPolicy for that version
        """
        pass
    
    @abstractmethod
    async def export_policy(self, policy_id: str, format: str = "yaml") -> str:
        """
        Export policy to string format.
        
        Args:
            policy_id: Policy to export
            format: Export format (yaml, json, etc)
            
        Returns:
            Serialized policy
        """
        pass