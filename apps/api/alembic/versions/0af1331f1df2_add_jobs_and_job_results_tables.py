"""add jobs and job_results tables

Revision ID: 0af1331f1df2
Revises: 001_initial_data
Create Date: 2025-08-15 16:20:21.313883

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0af1331f1df2'
down_revision: Union[str, None] = '001_initial_data'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    op.execute("DO $$ BEGIN CREATE TYPE jobstatus AS ENUM ('queued', 'running', 'succeeded', 'failed', 'cancelled', 'expired', 'retrying'); EXCEPTION WHEN duplicate_object THEN null; END $$")
    
    # Create jobs table
    op.create_table(
        'jobs',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('organization_id', sa.dialects.postgresql.UUID(as_uuid=True), index=True),
        sa.Column('task_name', sa.String(100), nullable=False, index=True),
        sa.Column('queue', sa.String(50), nullable=False, server_default='queue:free'),
        sa.Column('priority', sa.Integer(), server_default='5'),
        sa.Column('status', sa.Enum('queued', 'running', 'succeeded', 'failed', 'cancelled', 'expired', 'retrying', 
                                   name='jobstatus', create_type=False), 
                  nullable=False, server_default='queued', index=True),
        sa.Column('params_json', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('result_ref', sa.String(500)),
        sa.Column('error', sa.Text()),
        sa.Column('progress', sa.Float(), server_default='0.0'),
        sa.Column('message', sa.Text()),
        sa.Column('idempotency_key', sa.String(255), index=True),
        sa.Column('correlation_id', sa.String(100), index=True),
        sa.Column('celery_task_id', sa.String(255), unique=True, index=True),
        sa.Column('retry_count', sa.Integer(), server_default='0'),
        sa.Column('max_retries', sa.Integer(), server_default='3'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), index=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('started_at', sa.DateTime(timezone=True)),
        sa.Column('finished_at', sa.DateTime(timezone=True)),
        sa.Column('expires_at', sa.DateTime(timezone=True)),
        sa.Column('job_metadata', sa.JSON(), server_default='{}'),
    )
    
    # Add composite indexes and constraints
    op.create_unique_constraint('uq_user_idempotency', 'jobs', ['user_id', 'idempotency_key'])
    op.create_index('ix_jobs_user_status', 'jobs', ['user_id', 'status'])
    op.create_index('ix_jobs_created_at_desc', 'jobs', [sa.text('created_at DESC')])
    
    # Create job_results table
    op.create_table(
        'job_results',
        sa.Column('job_id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('result_json', sa.JSON()),
        sa.Column('object_uri', sa.String(500)),
        sa.Column('size_bytes', sa.Integer()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('job_results')
    op.drop_table('jobs')
    op.execute('DROP TYPE jobstatus')
