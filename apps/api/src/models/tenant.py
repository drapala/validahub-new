"""Tenant model for multi-tenancy."""

from sqlalchemy import Column, String, Boolean, Integer, JSON, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid

from src.db.base import Base
from src.models.utils import get_table_args


class TenantStatus(str, enum.Enum):
    """Tenant status enum."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    CANCELLED = "cancelled"


class TenantPlan(str, enum.Enum):
    """Tenant subscription plan."""
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class Tenant(Base):
    """Tenant model for multi-tenant architecture."""
    
    __tablename__ = "tenants"
    __table_args__ = get_table_args()
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Basic info
    name = Column(String(100), nullable=False)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    domain = Column(String(255), unique=True, nullable=True)
    
    # Company info
    company_name = Column(String(255), nullable=True)
    cnpj = Column(String(20), nullable=True)
    email = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    
    # Subscription
    plan = Column(SQLEnum(TenantPlan), default=TenantPlan.FREE, nullable=False)
    status = Column(SQLEnum(TenantStatus), default=TenantStatus.TRIAL, nullable=False)
    
    # Limits (based on plan)
    max_users = Column(Integer, default=5)
    max_validations_per_month = Column(Integer, default=1000)
    max_file_size_mb = Column(Integer, default=10)
    
    # Features
    features = Column(JSON, default=dict)
    settings = Column(JSON, default=dict)
    
    # Security
    is_verified = Column(Boolean, default=False)
    allowed_domains = Column(JSON, default=list)  # For email domain restrictions
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="tenant", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Tenant {self.slug}>"
    
    def has_feature(self, feature: str) -> bool:
        """Check if tenant has a specific feature enabled."""
        return self.features.get(feature, False) if self.features else False
    
    def can_add_user(self) -> bool:
        """Check if tenant can add more users."""
        current_users = len(self.users) if self.users else 0
        return current_users < self.max_users
    
    def get_plan_features(self) -> dict:
        """Get features available for the tenant's plan."""
        plan_features = {
            TenantPlan.FREE: {
                "api_access": False,
                "custom_rules": False,
                "webhooks": False,
                "priority_support": False,
                "sso": False
            },
            TenantPlan.STARTER: {
                "api_access": True,
                "custom_rules": False,
                "webhooks": False,
                "priority_support": False,
                "sso": False
            },
            TenantPlan.PRO: {
                "api_access": True,
                "custom_rules": True,
                "webhooks": True,
                "priority_support": True,
                "sso": False
            },
            TenantPlan.ENTERPRISE: {
                "api_access": True,
                "custom_rules": True,
                "webhooks": True,
                "priority_support": True,
                "sso": True,
                "dedicated_support": True,
                "custom_sla": True
            }
        }
        return plan_features.get(self.plan, {})