#!/usr/bin/env python3
"""
Seed script to populate database with initial/demo data.
Run: python apps/api/scripts/seed.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

from src.db.base import Base
from src.models.user import User
from src.models.job import Job, JobStatus
from src.models.file import File
from src.config import settings


def seed_database():
    """Populate database with initial demo data."""
    
    # Create engine and session
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check if already seeded
        existing_users = session.query(User).count()
        if existing_users > 0:
            print("✓ Database already contains data. Skipping seed.")
            return
        
        print("🌱 Seeding database...")
        
        # Create demo users
        demo_user = User(
            id=str(uuid.uuid4()),
            email="demo@validahub.com",
            username="demo_user",
            full_name="Demo User",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # secret
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        admin_user = User(
            id=str(uuid.uuid4()),
            email="admin@validahub.com",
            username="admin",
            full_name="Admin User",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # secret
            is_active=True,
            is_superuser=True,
            created_at=datetime.utcnow()
        )
        
        session.add_all([demo_user, admin_user])
        session.flush()
        
        # Create demo jobs
        job1 = Job(
            id=str(uuid.uuid4()),
            user_id=demo_user.id,
            status=JobStatus.COMPLETED,
            file_key="demos/sample_mercadolivre.csv",
            result={
                "total_rows": 100,
                "errors_found": 15,
                "corrections_applied": 15,
                "marketplace": "MERCADO_LIVRE"
            },
            created_at=datetime.utcnow()
        )
        
        job2 = Job(
            id=str(uuid.uuid4()),
            user_id=demo_user.id,
            status=JobStatus.PROCESSING,
            file_key="demos/sample_shopee.csv",
            created_at=datetime.utcnow()
        )
        
        session.add_all([job1, job2])
        session.flush()
        
        # Create demo files
        file1 = File(
            id=str(uuid.uuid4()),
            job_id=job1.id,
            s3_key="demos/sample_mercadolivre.csv",
            filename="produtos_ml.csv",
            size=5432,
            content_type="text/csv",
            created_at=datetime.utcnow()
        )
        
        session.add(file1)
        
        # Commit all changes
        session.commit()
        
        print("✅ Database seeded successfully!")
        print("\nDemo accounts created:")
        print("  📧 demo@validahub.com / password: secret")
        print("  👑 admin@validahub.com / password: secret")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()