from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from src.db.base import Base
from src.models.utils import get_table_args


class File(Base):
    __tablename__ = "files"
    __table_args__ = get_table_args()

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    s3_key = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    content_type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    job = relationship("Job", backref="files")