"""add_jobs_and_job_items_tables

Revision ID: 734c925959ed
Revises: 003_add_multi_tenant_tables
Create Date: 2025-08-28 17:58:01.433742

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '734c925959ed'
down_revision: Union[str, None] = '003_add_multi_tenant_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enums (if they don't exist)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE jobstatus AS ENUM ('pending', 'processing', 'success', 'failed', 'review', 'cancelled');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE jobchannel AS ENUM ('mercado_livre', 'amazon', 'b2w', 'magalu', 'shopee', 'via', 'casas_bahia');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE jobtype AS ENUM ('catalog_upload', 'price_update', 'stock_update', 'full_sync', 'validation_only');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE errorseverity AS ENUM ('low', 'medium', 'high', 'critical');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create jobs table
    op.create_table('jobs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('seller_id', sa.String(), nullable=False),
        sa.Column('seller_name', sa.String(), nullable=False),
        sa.Column('channel', sa.Enum('mercado_livre', 'amazon', 'b2w', 'magalu', 'shopee', 'via', 'casas_bahia', name='jobchannel'), nullable=False),
        sa.Column('type', sa.Enum('catalog_upload', 'price_update', 'stock_update', 'full_sync', 'validation_only', name='jobtype'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'processing', 'success', 'failed', 'review', 'cancelled', name='jobstatus'), nullable=False),
        sa.Column('total_items', sa.Integer(), nullable=True, default=0),
        sa.Column('processed_items', sa.Integer(), nullable=True, default=0),
        sa.Column('success_items', sa.Integer(), nullable=True, default=0),
        sa.Column('failed_items', sa.Integer(), nullable=True, default=0),
        sa.Column('warning_items', sa.Integer(), nullable=True, default=0),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('avg_item_time_ms', sa.Float(), nullable=True),
        sa.Column('p95_time_ms', sa.Float(), nullable=True),
        sa.Column('p99_time_ms', sa.Float(), nullable=True),
        sa.Column('error_count', sa.Integer(), nullable=True, default=0),
        sa.Column('warning_count', sa.Integer(), nullable=True, default=0),
        sa.Column('severity', sa.Enum('low', 'medium', 'high', 'critical', name='errorseverity'), nullable=True),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('file_name', sa.String(), nullable=True),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True),
        sa.Column('file_url', sa.String(), nullable=True),
        sa.Column('idempotency_key', sa.String(length=255), nullable=True),
        sa.Column('reprocess_count', sa.Integer(), nullable=True, default=0),
        sa.Column('parent_job_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('job_metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['parent_job_id'], ['jobs.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for jobs
    op.create_index('idx_jobs_tenant_created', 'jobs', ['tenant_id', 'created_at'], unique=False)
    op.create_index('idx_jobs_tenant_seller', 'jobs', ['tenant_id', 'seller_id'], unique=False)
    op.create_index('idx_jobs_tenant_status', 'jobs', ['tenant_id', 'status'], unique=False)
    op.create_index(op.f('ix_jobs_created_at'), 'jobs', ['created_at'], unique=False)
    op.create_index(op.f('ix_jobs_idempotency_key'), 'jobs', ['idempotency_key'], unique=False)
    op.create_index(op.f('ix_jobs_seller_id'), 'jobs', ['seller_id'], unique=False)
    op.create_index(op.f('ix_jobs_status'), 'jobs', ['status'], unique=False)
    op.create_index(op.f('ix_jobs_tenant_id'), 'jobs', ['tenant_id'], unique=False)
    op.create_index('uq_tenant_idempotency', 'jobs', ['tenant_id', 'idempotency_key'], unique=True, postgresql_where=sa.text('idempotency_key IS NOT NULL'))
    
    # Create job_items table
    op.create_table('job_items',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('job_id', sa.String(), nullable=False),
        sa.Column('sku', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('status', sa.Enum('pending', 'processing', 'success', 'failed', 'review', 'cancelled', name='jobstatus'), nullable=False),
        sa.Column('field_errors', sa.JSON(), nullable=True),
        sa.Column('business_errors', sa.JSON(), nullable=True),
        sa.Column('warnings', sa.JSON(), nullable=True),
        sa.Column('suggestions', sa.JSON(), nullable=True),
        sa.Column('error_codes', sa.JSON(), nullable=True),
        sa.Column('error_categories', sa.JSON(), nullable=True),
        sa.Column('original_data', sa.JSON(), nullable=True),
        sa.Column('corrected_data', sa.JSON(), nullable=True),
        sa.Column('corrections_applied', sa.JSON(), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for job_items
    op.create_index('idx_job_items_job_sku', 'job_items', ['job_id', 'sku'], unique=False)
    op.create_index('idx_job_items_job_status', 'job_items', ['job_id', 'status'], unique=False)
    op.create_index(op.f('ix_job_items_job_id'), 'job_items', ['job_id'], unique=False)
    op.create_index(op.f('ix_job_items_sku'), 'job_items', ['sku'], unique=False)


def downgrade() -> None:
    # Drop job_items
    op.drop_index(op.f('ix_job_items_sku'), table_name='job_items')
    op.drop_index(op.f('ix_job_items_job_id'), table_name='job_items')
    op.drop_index('idx_job_items_job_status', table_name='job_items')
    op.drop_index('idx_job_items_job_sku', table_name='job_items')
    op.drop_table('job_items')
    
    # Drop jobs
    op.drop_index('uq_tenant_idempotency', table_name='jobs')
    op.drop_index(op.f('ix_jobs_tenant_id'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_status'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_seller_id'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_idempotency_key'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_created_at'), table_name='jobs')
    op.drop_index('idx_jobs_tenant_status', table_name='jobs')
    op.drop_index('idx_jobs_tenant_seller', table_name='jobs')
    op.drop_index('idx_jobs_tenant_created', table_name='jobs')
    op.drop_table('jobs')
    
    # Drop enums
    op.execute("DROP TYPE IF EXISTS jobstatus")
    op.execute("DROP TYPE IF EXISTS jobchannel")
    op.execute("DROP TYPE IF EXISTS jobtype")
    op.execute("DROP TYPE IF EXISTS errorseverity")