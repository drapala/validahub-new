"""add telemetry events table

Revision ID: 002_add_telemetry_events
Revises: 0af1331f1df2
Create Date: 2025-08-16 12:00:00.000000

"""
from typing import Sequence, Union
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_add_telemetry_events'
down_revision: Union[str, None] = '0af1331f1df2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def create_monthly_partitions(start_year: int, start_month: int, num_months: int):
    """Create monthly partitions for telemetry_events table."""
    current = date(start_year, start_month, 1)
    
    for _ in range(num_months):
        next_month = current + relativedelta(months=1)
        partition_name = f"telemetry_events_p{current.strftime('%Y%m')}"
        
        op.execute(f"""
            CREATE TABLE {partition_name} PARTITION OF telemetry_events
            FOR VALUES FROM ('{current.strftime('%Y-%m-%d')}') TO ('{next_month.strftime('%Y-%m-%d')}');
        """)
        
        current = next_month


def upgrade() -> None:
    # Create telemetry_events table with partitioning by created_at
    op.execute("""
        CREATE TABLE telemetry_events (
            event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            event_name VARCHAR(100) NOT NULL,
            version VARCHAR(10) NOT NULL DEFAULT 'v1',
            timestamp TIMESTAMPTZ NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            
            -- Partitioning and correlation
            partition_key VARCHAR(255) NOT NULL,
            correlation_id UUID,
            parent_id UUID,
            
            -- Job context
            job_id UUID,
            job_execution_id UUID,  -- For retry tracking
            task_name VARCHAR(100),
            
            -- Business context
            marketplace VARCHAR(50),
            category VARCHAR(50),
            region VARCHAR(50),
            
            -- Event payload
            payload JSONB NOT NULL,
            metrics JSONB,
            error JSONB
        ) PARTITION BY RANGE (created_at);
    """)
    
    # Create indexes
    op.create_index('idx_telemetry_events_event_name', 'telemetry_events', ['event_name'])
    op.create_index('idx_telemetry_events_job_id', 'telemetry_events', ['job_id'])
    op.create_index('idx_telemetry_events_correlation_id', 'telemetry_events', ['correlation_id'])
    op.create_index('idx_telemetry_events_partition_key', 'telemetry_events', ['partition_key'])
    op.create_index('idx_telemetry_events_created_at', 'telemetry_events', ['created_at'])
    op.create_index('idx_telemetry_events_marketplace_category', 'telemetry_events', ['marketplace', 'category'])
    
    # Create GIN index for JSONB columns
    op.execute("CREATE INDEX idx_telemetry_events_payload ON telemetry_events USING GIN (payload)")
    op.execute("CREATE INDEX idx_telemetry_events_metrics ON telemetry_events USING GIN (metrics)")
    
    # Create monthly partitions for current year and next 6 months
    now = datetime.now()
    # Create partitions for past 3 months, current month, and next 12 months
    start_date = now - relativedelta(months=3)
    create_monthly_partitions(start_date.year, start_date.month, 16)
    
    # Create a default partition for out-of-range data
    op.execute("""
        CREATE TABLE telemetry_events_default PARTITION OF telemetry_events
        DEFAULT;
    """)
    
    # Create function to automatically create new partitions
    op.execute("""
        CREATE OR REPLACE FUNCTION create_telemetry_partition()
        RETURNS void AS $$
        DECLARE
            start_date date;
            end_date date;
            partition_name text;
        BEGIN
            -- Create partition for next month if it doesn't exist
            start_date := date_trunc('month', CURRENT_DATE + interval '1 month');
            end_date := start_date + interval '1 month';
            partition_name := 'telemetry_events_p' || to_char(start_date, 'YYYYMM');
            
            -- Check if partition already exists
            IF NOT EXISTS (
                SELECT 1 FROM pg_class 
                WHERE relname = partition_name
            ) THEN
                EXECUTE format(
                    'CREATE TABLE %I PARTITION OF telemetry_events FOR VALUES FROM (%L) TO (%L)',
                    partition_name,
                    start_date,
                    end_date
                );
                RAISE NOTICE 'Created partition %', partition_name;
            END IF;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Create function to drop old partitions (keep last 6 months)
    op.execute("""
        CREATE OR REPLACE FUNCTION drop_old_telemetry_partitions()
        RETURNS void AS $$
        DECLARE
            partition_record record;
            cutoff_date date;
        BEGIN
            cutoff_date := date_trunc('month', CURRENT_DATE - interval '6 months');
            
            FOR partition_record IN
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public' 
                AND tablename LIKE 'telemetry_events_p%'
                AND tablename != 'telemetry_events_default'
            LOOP
                -- Extract date from partition name (format: telemetry_events_pYYYYMM)
                IF substring(partition_record.tablename from 20 for 6)::date < cutoff_date THEN
                    EXECUTE format('DROP TABLE %I', partition_record.tablename);
                    RAISE NOTICE 'Dropped old partition %', partition_record.tablename;
                END IF;
            END LOOP;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Create aggregated metrics table for dashboard queries
    op.create_table(
        'telemetry_metrics_hourly',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('hour', sa.DateTime(timezone=True), nullable=False),
        sa.Column('marketplace', sa.String(50), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('region', sa.String(50), nullable=False, server_default='default'),
        sa.Column('task_name', sa.String(100), nullable=False),
        
        # Counters
        sa.Column('jobs_started', sa.Integer(), server_default='0'),
        sa.Column('jobs_completed', sa.Integer(), server_default='0'),
        sa.Column('jobs_failed', sa.Integer(), server_default='0'),
        sa.Column('jobs_retried', sa.Integer(), server_default='0'),
        
        # Metrics
        sa.Column('total_rows_processed', sa.BigInteger(), server_default='0'),
        sa.Column('total_errors', sa.BigInteger(), server_default='0'),
        sa.Column('total_warnings', sa.BigInteger(), server_default='0'),
        sa.Column('avg_latency_ms', sa.Float(), server_default='0'),
        sa.Column('p95_latency_ms', sa.Float(), server_default='0'),
        sa.Column('p99_latency_ms', sa.Float(), server_default='0'),
        sa.Column('total_payload_bytes', sa.BigInteger(), server_default='0'),
        
        # Error rates
        sa.Column('avg_error_rate', sa.Float(), server_default='0'),
        sa.Column('avg_warning_rate', sa.Float(), server_default='0'),
        
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now())
    )
    
    # Create unique constraint for aggregation key
    op.create_index(
        'idx_telemetry_metrics_hourly_unique',
        'telemetry_metrics_hourly',
        ['hour', 'marketplace', 'category', 'region', 'task_name'],
        unique=True
    )
    
    # Create index for time-based queries
    op.create_index('idx_telemetry_metrics_hourly_hour', 'telemetry_metrics_hourly', ['hour'])
    
    # Create a view for recent events (last 24 hours)
    op.execute("""
        CREATE VIEW telemetry_events_recent AS
        SELECT * FROM telemetry_events
        WHERE created_at >= NOW() - INTERVAL '24 hours'
        ORDER BY created_at DESC;
    """)
    
    # Create a materialized view for daily stats
    op.execute("""
        CREATE MATERIALIZED VIEW telemetry_daily_stats AS
        SELECT 
            DATE(created_at) as date,
            marketplace,
            category,
            region,
            event_name,
            COUNT(*) as event_count,
            COUNT(DISTINCT job_id) as unique_jobs,
            AVG((metrics->>'latency_ms')::float) as avg_latency_ms,
            SUM((metrics->>'total_rows')::int) as total_rows,
            SUM((metrics->>'error_rows')::int) as total_errors
        FROM telemetry_events
        WHERE created_at >= NOW() - INTERVAL '30 days'
        GROUP BY DATE(created_at), marketplace, category, region, event_name;
    """)
    
    # Create index on materialized view
    op.execute("""
        CREATE INDEX idx_telemetry_daily_stats_date 
        ON telemetry_daily_stats(date DESC);
    """)


def downgrade() -> None:
    # Drop functions
    op.execute("DROP FUNCTION IF EXISTS create_telemetry_partition()")
    op.execute("DROP FUNCTION IF EXISTS drop_old_telemetry_partitions()")
    
    # Drop materialized view
    op.execute("DROP MATERIALIZED VIEW IF EXISTS telemetry_daily_stats")
    
    # Drop view
    op.execute("DROP VIEW IF EXISTS telemetry_events_recent")
    
    # Drop aggregated metrics table
    op.drop_table('telemetry_metrics_hourly')
    
    # Drop all partitions
    op.execute("""
        DO $$
        DECLARE
            partition_name text;
        BEGIN
            FOR partition_name IN
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public' 
                AND (tablename LIKE 'telemetry_events_p%' OR tablename = 'telemetry_events_default')
            LOOP
                EXECUTE format('DROP TABLE IF EXISTS %I', partition_name);
            END LOOP;
        END $$;
    """)
    
    # Drop main table
    op.execute("DROP TABLE IF EXISTS telemetry_events")