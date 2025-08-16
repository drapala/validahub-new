#!/usr/bin/env python3
"""
Telemetry partition maintenance script.

This script should be run monthly (e.g., via cron) to:
1. Create new partitions for upcoming months
2. Drop old partitions to manage disk space
3. Refresh materialized views

Usage:
    python scripts/telemetry_maintenance.py

Cron example (run on the 1st of each month at 2 AM):
    0 2 1 * * /usr/bin/python3 /path/to/scripts/telemetry_maintenance.py
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.base import SessionLocal, engine
from sqlalchemy import text

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_next_month_partition():
    """Create partition for next month if it doesn't exist."""
    with engine.connect() as conn:
        try:
            result = conn.execute(text("SELECT create_telemetry_partition()"))
            conn.commit()
            logger.info("Successfully checked/created next month's partition")
        except Exception as e:
            logger.error(f"Error creating partition: {e}")
            raise


def drop_old_partitions():
    """Drop partitions older than 6 months."""
    with engine.connect() as conn:
        try:
            result = conn.execute(text("SELECT drop_old_telemetry_partitions()"))
            conn.commit()
            logger.info("Successfully dropped old partitions")
        except Exception as e:
            logger.error(f"Error dropping old partitions: {e}")
            raise


def refresh_materialized_views():
    """Refresh materialized views for reporting."""
    with engine.connect() as conn:
        try:
            # Refresh daily stats view
            conn.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY telemetry_daily_stats"))
            conn.commit()
            logger.info("Successfully refreshed telemetry_daily_stats view")
        except Exception as e:
            logger.error(f"Error refreshing materialized views: {e}")
            raise


def vacuum_telemetry_tables():
    """Vacuum telemetry tables to reclaim space and update statistics."""
    with engine.connect() as conn:
        try:
            # Get list of all telemetry partitions
            result = conn.execute(text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public' 
                AND tablename LIKE 'telemetry_events%'
            """))
            
            tables = [row[0] for row in result]
            
            # Vacuum each partition
            for table in tables:
                conn.execute(text(f"VACUUM ANALYZE {table}"))
                logger.info(f"Vacuumed table: {table}")
            
            conn.commit()
            logger.info("Successfully vacuumed all telemetry tables")
        except Exception as e:
            logger.error(f"Error vacuuming tables: {e}")
            raise


def main():
    """Run all maintenance tasks."""
    logger.info("Starting telemetry maintenance")
    
    try:
        # Create partitions for next month
        create_next_month_partition()
        
        # Drop old partitions (keep last 6 months)
        drop_old_partitions()
        
        # Refresh materialized views
        refresh_materialized_views()
        
        # Vacuum tables
        vacuum_telemetry_tables()
        
        logger.info("Telemetry maintenance completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Telemetry maintenance failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())