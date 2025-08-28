"""Base model for all database models."""

from datetime import datetime
from sqlalchemy import Column, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr
import uuid

Base = declarative_base()


class BaseModel(Base):
    """Abstract base model with common fields."""
    
    __abstract__ = True
    
    @declared_attr
    def __tablename__(cls):
        """Generate tablename from class name."""
        return cls.__name__.lower()
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)