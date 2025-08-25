from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from src.db.base import Base

# Conditional import for test settings
try:
    from src.test_settings import is_test_environment, BASE_MODEL_CONFIG
    if is_test_environment():
        table_args = BASE_MODEL_CONFIG.get("__table_args__", {})
    else:
        table_args = {}
except ImportError:
    table_args = {}


class File(Base):
    __tablename__ = "files"
    __table_args__ = table_args

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    s3_key = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    content_type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    job = relationship("Job", backref="files")