#!/usr/bin/env python3
"""
Seed script for development database.
Creates initial tenants, users, and API keys for testing.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import settings
from src.models.tenant import Tenant, TenantPlan, TenantStatus
from src.models.user import User, UserRole
from src.models.api_key import ApiKey
from src.services.auth_service import AuthService
import secrets
import hashlib


def generate_api_key():
    """Generate a secure API key."""
    key = f"vhb_{secrets.token_urlsafe(32)}"
    prefix = key[:10]
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    return key, prefix, key_hash


def main():
    """Seed the database with initial data."""
    # Create database engine and session
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    auth_service = AuthService()
    
    try:
        # Check if data already exists
        existing_tenant = db.query(Tenant).filter_by(slug="demo-company").first()
        if existing_tenant:
            print("Seed data already exists. Skipping...")
            return
        
        print("Creating seed data...")
        
        # Create demo tenant
        demo_tenant = Tenant(
            id="tenant_demo",
            name="Demo Company",
            slug="demo-company",
            domain="demo.validahub.com",
            company_name="Demo Company Ltda",
            cnpj="00.000.000/0001-00",
            email="admin@demo.validahub.com",
            phone="+55 11 98765-4321",
            plan=TenantPlan.PRO,
            status=TenantStatus.ACTIVE,
            max_users=20,
            max_validations_per_month=10000,
            max_file_size_mb=100,
            features={
                "bulk_upload": True,
                "api_access": True,
                "custom_rules": True,
                "white_label": False,
                "priority_support": True,
                "data_export": True,
                "webhooks": True,
                "sso": False
            },
            settings={
                "theme": "light",
                "notifications": {
                    "email": True,
                    "webhook": True
                },
                "security": {
                    "require_mfa": False,
                    "password_policy": "standard"
                }
            },
            is_verified=True,
            allowed_domains=["demo.validahub.com", "demo.com"]
        )
        db.add(demo_tenant)
        
        # Create trial tenant
        trial_tenant = Tenant(
            id="tenant_trial",
            name="Trial Company",
            slug="trial-company",
            email="trial@example.com",
            plan=TenantPlan.FREE,
            status=TenantStatus.TRIAL,
            max_users=3,
            max_validations_per_month=100,
            max_file_size_mb=10,
            features={
                "bulk_upload": False,
                "api_access": False,
                "custom_rules": False,
                "white_label": False,
                "priority_support": False,
                "data_export": True,
                "webhooks": False,
                "sso": False
            },
            is_verified=False
        )
        db.add(trial_tenant)
        
        # Create users for demo tenant
        demo_owner = User(
            id="user_demo_owner",
            tenant_id="tenant_demo",
            email="owner@demo.validahub.com",
            hashed_password=auth_service.hash_password("Demo@2024"),
            name="João Silva",
            phone="+55 11 98765-4321",
            department="Executive",
            role=UserRole.OWNER,
            is_active=True,
            is_verified=True,
            last_login=datetime.now(timezone.utc),
            two_factor_enabled=False
        )
        db.add(demo_owner)
        
        demo_admin = User(
            id="user_demo_admin",
            tenant_id="tenant_demo",
            email="admin@demo.validahub.com",
            hashed_password=auth_service.hash_password("Admin@2024"),
            name="Maria Santos",
            phone="+55 11 98765-4322",
            department="Operations",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
            two_factor_enabled=False
        )
        db.add(demo_admin)
        
        demo_manager = User(
            id="user_demo_manager",
            tenant_id="tenant_demo",
            email="manager@demo.validahub.com",
            hashed_password=auth_service.hash_password("Manager@2024"),
            name="Pedro Costa",
            department="Sales",
            role=UserRole.MANAGER,
            is_active=True,
            is_verified=True,
            two_factor_enabled=False
        )
        db.add(demo_manager)
        
        demo_member = User(
            id="user_demo_member",
            tenant_id="tenant_demo",
            email="member@demo.validahub.com",
            hashed_password=auth_service.hash_password("Member@2024"),
            name="Ana Oliveira",
            department="Marketing",
            role=UserRole.MEMBER,
            is_active=True,
            is_verified=True,
            two_factor_enabled=False
        )
        db.add(demo_member)
        
        demo_viewer = User(
            id="user_demo_viewer",
            tenant_id="tenant_demo",
            email="viewer@demo.validahub.com",
            hashed_password=auth_service.hash_password("Viewer@2024"),
            name="Carlos Lima",
            department="Finance",
            role=UserRole.VIEWER,
            is_active=True,
            is_verified=False,
            two_factor_enabled=False
        )
        db.add(demo_viewer)
        
        # Create trial tenant user
        trial_owner = User(
            id="user_trial_owner",
            tenant_id="tenant_trial",
            email="trial@example.com",
            hashed_password=auth_service.hash_password("Trial@2024"),
            name="Test User",
            role=UserRole.OWNER,
            is_active=True,
            is_verified=False,
            two_factor_enabled=False
        )
        db.add(trial_owner)
        
        # Create API keys
        api_key_full, prefix_full, hash_full = generate_api_key()
        demo_api_key_full = ApiKey(
            id="apikey_demo_full",
            tenant_id="tenant_demo",
            name="Full Access Key",
            description="API key with full access to all endpoints",
            key_prefix=prefix_full,
            key_hash=hash_full,
            scopes=["read:all", "write:all", "delete:all"],
            is_active=True,
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),
            rate_limit=1000
        )
        db.add(demo_api_key_full)
        
        api_key_read, prefix_read, hash_read = generate_api_key()
        demo_api_key_readonly = ApiKey(
            id="apikey_demo_readonly",
            tenant_id="tenant_demo",
            name="Read Only Key",
            description="API key with read-only access",
            key_prefix=prefix_read,
            key_hash=hash_read,
            scopes=["read:all"],
            is_active=True,
            expires_at=datetime.now(timezone.utc) + timedelta(days=180),
            rate_limit=500
        )
        db.add(demo_api_key_readonly)
        
        api_key_webhook, prefix_webhook, hash_webhook = generate_api_key()
        demo_api_key_webhook = ApiKey(
            id="apikey_demo_webhook",
            tenant_id="tenant_demo",
            name="Webhook Key",
            description="API key for webhook integrations",
            key_prefix=prefix_webhook,
            key_hash=hash_webhook,
            scopes=["webhook:send", "read:jobs", "read:results"],
            is_active=True,
            rate_limit=100
        )
        db.add(demo_api_key_webhook)
        
        # Commit all changes
        db.commit()
        
        print("\n✅ Seed data created successfully!")
        print("\n📋 Created tenants:")
        print(f"  - Demo Company (slug: demo-company) - PRO plan")
        print(f"  - Trial Company (slug: trial-company) - FREE plan")
        
        print("\n👥 Created users for Demo Company:")
        print(f"  - owner@demo.validahub.com (password: Demo@2024) - OWNER")
        print(f"  - admin@demo.validahub.com (password: Admin@2024) - ADMIN")
        print(f"  - manager@demo.validahub.com (password: Manager@2024) - MANAGER")
        print(f"  - member@demo.validahub.com (password: Member@2024) - MEMBER")
        print(f"  - viewer@demo.validahub.com (password: Viewer@2024) - VIEWER")
        
        print("\n👥 Created users for Trial Company:")
        print(f"  - trial@example.com (password: Trial@2024) - OWNER")
        
        print("\n🔑 Created API keys for Demo Company:")
        print(f"  - Full Access Key: {api_key_full}")
        print(f"  - Read Only Key: {api_key_read}")
        print(f"  - Webhook Key: {api_key_webhook}")
        
        print("\n⚠️  Save these API keys securely - they cannot be retrieved again!")
        
    except Exception as e:
        print(f"❌ Error creating seed data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()