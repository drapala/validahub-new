"""add multi tenant tables

Revision ID: 003_add_multi_tenant_tables
Revises: 002_add_telemetry_events
Create Date: 2025-08-28 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003_add_multi_tenant_tables'
down_revision: Union[str, None] = '002_add_telemetry_events'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create tenants table
    op.create_table('tenants',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=50), nullable=False),
        sa.Column('domain', sa.String(length=255), nullable=True),
        sa.Column('company_name', sa.String(length=255), nullable=True),
        sa.Column('cnpj', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('plan', sa.Enum('FREE', 'STARTER', 'PRO', 'ENTERPRISE', name='tenantplan'), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'SUSPENDED', 'TRIAL', 'CANCELLED', name='tenantstatus'), nullable=False),
        sa.Column('max_users', sa.Integer(), nullable=True),
        sa.Column('max_validations_per_month', sa.Integer(), nullable=True),
        sa.Column('max_file_size_mb', sa.Integer(), nullable=True),
        sa.Column('features', sa.JSON(), nullable=True),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('allowed_domains', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('domain'),
        sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_tenants_slug'), 'tenants', ['slug'], unique=True)
    op.create_index(op.f('ix_tenants_email'), 'tenants', ['email'], unique=False)
    
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('role', sa.Enum('OWNER', 'ADMIN', 'MANAGER', 'MEMBER', 'VIEWER', name='userrole'), nullable=False),
        sa.Column('custom_permissions', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('password_reset_token', sa.String(length=255), nullable=True),
        sa.Column('password_reset_expires', sa.DateTime(timezone=True), nullable=True),
        sa.Column('email_verification_token', sa.String(length=255), nullable=True),
        sa.Column('two_factor_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('two_factor_secret', sa.String(length=255), nullable=True),
        sa.Column('preferences', sa.JSON(), nullable=True),
        sa.Column('refresh_token', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)
    op.create_index(op.f('ix_users_tenant_id'), 'users', ['tenant_id'], unique=False)
    op.create_index('ix_users_tenant_email', 'users', ['tenant_id', 'email'], unique=True)
    
    # Create api_keys table
    op.create_table('api_keys',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('key_prefix', sa.String(length=10), nullable=False),
        sa.Column('key_hash', sa.String(length=255), nullable=False),
        sa.Column('scopes', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rate_limit', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_api_keys_key_hash'), 'api_keys', ['key_hash'], unique=True)
    op.create_index(op.f('ix_api_keys_tenant_id'), 'api_keys', ['tenant_id'], unique=False)
    
    # Add tenant_id to jobs table if it exists
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'jobs') THEN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                             WHERE table_name = 'jobs' AND column_name = 'tenant_id') THEN
                    ALTER TABLE jobs ADD COLUMN tenant_id VARCHAR;
                    ALTER TABLE jobs ADD COLUMN created_by_user_id VARCHAR;
                    CREATE INDEX ix_jobs_tenant_id ON jobs(tenant_id);
                END IF;
            END IF;
        END $$;
    """)
    
    # Add tenant_id to files table if it exists
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'files') THEN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                             WHERE table_name = 'files' AND column_name = 'tenant_id') THEN
                    ALTER TABLE files ADD COLUMN tenant_id VARCHAR;
                    CREATE INDEX ix_files_tenant_id ON files(tenant_id);
                END IF;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    # Drop tenant_id from existing tables
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'files' AND column_name = 'tenant_id') THEN
                ALTER TABLE files DROP COLUMN tenant_id;
            END IF;
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'jobs' AND column_name = 'tenant_id') THEN
                ALTER TABLE jobs DROP COLUMN tenant_id;
                ALTER TABLE jobs DROP COLUMN created_by_user_id;
            END IF;
        END $$;
    """)
    
    # Drop tables
    op.drop_table('api_keys')
    op.drop_table('users')
    op.drop_table('tenants')
    
    # Drop enums
    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("DROP TYPE IF EXISTS tenantstatus")
    op.execute("DROP TYPE IF EXISTS tenantplan")