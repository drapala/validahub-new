"""Add initial demo data

Revision ID: 001_initial_data
Revises: 
Create Date: 2024-01-14 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime
import uuid


# revision identifiers
revision = '001_initial_data'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Add initial demo data to database."""
    
    # Create users table if not exists
    op.create_table(
        'users',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('email', sa.String(), unique=True, nullable=False),
        sa.Column('username', sa.String(), unique=True, nullable=False),
        sa.Column('full_name', sa.String()),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_superuser', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), onupdate=datetime.utcnow)
    )
    
    # Create jobs table
    op.create_table(
        'jobs',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), sa.ForeignKey('users.id')),
        sa.Column('tenant_id', sa.String()),
        sa.Column('status', sa.Enum('pending', 'processing', 'completed', 'failed', name='jobstatus')),
        sa.Column('file_key', sa.String(), nullable=False),
        sa.Column('result', sa.JSON()),
        sa.Column('error', sa.String()),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), onupdate=datetime.utcnow)
    )
    
    # Create files table
    op.create_table(
        'files',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('job_id', sa.String(), sa.ForeignKey('jobs.id')),
        sa.Column('s3_key', sa.String(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('size', sa.Integer()),
        sa.Column('content_type', sa.String()),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow)
    )
    
    # Insert demo data
    op.bulk_insert(
        sa.table('users',
            sa.column('id'),
            sa.column('email'),
            sa.column('username'),
            sa.column('full_name'),
            sa.column('hashed_password'),
            sa.column('is_active'),
            sa.column('is_superuser'),
            sa.column('created_at')
        ),
        [
            {
                'id': str(uuid.uuid4()),
                'email': 'demo@validahub.com',
                'username': 'demo_user',
                'full_name': 'Demo User',
                'hashed_password': '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
                'is_active': True,
                'is_superuser': False,
                'created_at': datetime.utcnow()
            }
        ]
    )


def downgrade():
    """Remove initial data and tables."""
    op.drop_table('files')
    op.drop_table('jobs')
    op.drop_table('users')
    op.execute('DROP TYPE IF EXISTS jobstatus')