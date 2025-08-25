from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
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


class User(Base):
    __tablename__ = "users"
    __table_args__ = table_args

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    tenant_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())