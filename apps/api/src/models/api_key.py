"""API Key model for tenant API access."""

from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import secrets
import hashlib
import uuid

from src.db.base import Base
from src.models.utils import get_table_args


class ApiKey(Base):
    """API Key for programmatic access."""
    
    __tablename__ = "api_keys"
    __table_args__ = get_table_args()
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Tenant association
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Key details
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    
    # The key itself (hashed for security)
    key_prefix = Column(String(10), nullable=False)  # First 10 chars for identification
    key_hash = Column(String(255), nullable=False, unique=True, index=True)
    
    # Permissions
    scopes = Column(JSON, default=list)  # List of allowed scopes
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Usage tracking
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    usage_count = Column(String(20), default="0")
    
    # Expiration
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Rate limiting (requests per minute)
    rate_limit = Column(String(10), default="60")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant", back_populates="api_keys")
    
    def __repr__(self):
        return f"<ApiKey {self.name} for tenant {self.tenant_id}>"
    
    @classmethod
    def generate_key(cls) -> tuple[str, str]:
        """Generate a new API key.
        
        Returns:
            tuple: (full_key, key_hash) - full_key should be shown once to user
        """
        # Generate a secure random key
        key = f"vk_{secrets.token_urlsafe(48)}"  # vk_ prefix for ValidaHub Key
        
        # Hash the key for storage
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        
        return key, key_hash
    
    @classmethod
    def hash_key(cls, key: str) -> str:
        """Hash an API key for comparison."""
        return hashlib.sha256(key.encode()).hexdigest()
    
    def has_scope(self, scope: str) -> bool:
        """Check if the API key has a specific scope."""
        return scope in (self.scopes or [])
    
    def is_valid(self) -> bool:
        """Check if the API key is valid and not expired."""
        if not self.is_active:
            return False
        
        if self.expires_at:
            from datetime import datetime, timezone
            return datetime.now(timezone.utc) < self.expires_at
        
        return True
    
    def increment_usage(self):
        """Increment usage count."""
        current = int(self.usage_count or 0)
        self.usage_count = str(current + 1)
        
        from datetime import datetime, timezone
        self.last_used_at = datetime.now(timezone.utc)