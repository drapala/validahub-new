"""User model with multi-tenant support."""

from sqlalchemy import Column, String, Boolean, ForeignKey, Enum as SQLEnum, DateTime, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
import enum
import uuid
from datetime import datetime

from src.db.base import Base
from src.models.utils import get_table_args


class UserRole(str, enum.Enum):
    """User roles within a tenant."""
    OWNER = "owner"  # Tenant owner, full access
    ADMIN = "admin"  # Can manage users and settings  
    MANAGER = "manager"  # Can manage validations and data
    MEMBER = "member"  # Basic access to validations
    VIEWER = "viewer"  # Read-only access


class User(Base):
    """User model with tenant association."""
    
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint('email', 'tenant_id', name='_email_tenant_uc'),
        *get_table_args()
    )
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Tenant association (REQUIRED for multi-tenancy)
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Authentication
    email = Column(String, nullable=False, index=True)
    hashed_password = Column(String, nullable=True)  # Nullable for SSO users
    
    # Profile
    name = Column(String(100), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    phone = Column(String(20), nullable=True)
    department = Column(String(100), nullable=True)
    
    # Role & Permissions
    role = Column(SQLEnum(UserRole), default=UserRole.MEMBER, nullable=False)
    custom_permissions = Column(JSON, default=dict)  # Override permissions
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Security
    last_login = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(String(10), default="0", nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    
    # 2FA
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255), nullable=True)
    
    # Tokens
    refresh_token = Column(String(500), nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)
    email_verification_token = Column(String(255), nullable=True)
    
    # Preferences
    preferences = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    
    def __repr__(self):
        return f"<User {self.email} in tenant {self.tenant_id}>"
    
    def set_password(self, password: str):
        """Set password hash."""
        self.hashed_password = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check password against hash."""
        if not self.hashed_password:
            return False
        return check_password_hash(self.hashed_password, password)
    
    def can_access_tenant(self, tenant_id: str) -> bool:
        """Check if user can access a tenant."""
        return self.tenant_id == tenant_id
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission."""
        # Owner has all permissions
        if self.role == UserRole.OWNER:
            return True
        
        # Check role-based permissions
        role_permissions = {
            UserRole.ADMIN: ["manage_users", "manage_settings", "manage_data", "view_data"],
            UserRole.MANAGER: ["manage_data", "view_data"],
            UserRole.MEMBER: ["create_data", "view_data"],
            UserRole.VIEWER: ["view_data"]
        }
        
        if permission in role_permissions.get(self.role, []):
            return True
        
        # Check custom permissions
        return self.custom_permissions.get(permission, False) if self.custom_permissions else False
    
    def is_admin_or_owner(self) -> bool:
        """Check if user is admin or owner."""
        return self.role in [UserRole.OWNER, UserRole.ADMIN]