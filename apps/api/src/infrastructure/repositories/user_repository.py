"""
Repository for User entities.
Handles all database operations for users.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from core.logging_config import get_logger

from .base_repository import BaseRepository
from models.user import User
from core.result import Result, Ok, Err

logger = get_logger(__name__)


class UserRepository(BaseRepository[User]):
    """
    Repository for User entities.
    
    This repository extends BaseRepository with user-specific
    operations like finding by email, tenant operations, etc.
    """
    
    def __init__(self, db: Session):
        """
        Initialize UserRepository.
        
        Args:
            db: Database session
        """
        super().__init__(User, db)
    
    def find_by_email(self, email: str) -> Result[Optional[User], str]:
        """
        Find user by email address.
        
        Args:
            email: User's email address
            
        Returns:
            Result containing user or None if not found
        """
        try:
            user = self.db.query(User).filter(
                User.email == email.lower()
            ).first()
            return Ok(user)
        except Exception as e:
            logger.error(f"Failed to find user by email {email}: {e}")
            return Err(str(e))
    
    def find_by_tenant(
        self, 
        tenant_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> Result[List[User], str]:
        """
        Find all users belonging to a tenant.
        
        Args:
            tenant_id: Tenant ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Result containing list of users or error
        """
        try:
            users = self.db.query(User).filter(
                User.tenant_id == tenant_id
            ).offset(skip).limit(limit).all()
            return Ok(users)
        except Exception as e:
            logger.error(f"Failed to find users by tenant {tenant_id}: {e}")
            return Err(str(e))
    
    def find_active_users(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> Result[List[User], str]:
        """
        Find all active users.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Result containing list of active users or error
        """
        try:
            users = self.db.query(User).filter(
                User.is_active == True
            ).offset(skip).limit(limit).all()
            return Ok(users)
        except Exception as e:
            logger.error(f"Failed to find active users: {e}")
            return Err(str(e))
    
    def update_password(
        self, 
        user_id: str, 
        hashed_password: str
    ) -> Result[bool, str]:
        """
        Update user's password.
        
        Args:
            user_id: User ID
            hashed_password: New hashed password
            
        Returns:
            Result containing success boolean or error
        """
        try:
            user_result = self.get_by_id(user_id)
            if user_result.is_err():
                return Err(user_result.unwrap_err())
            
            user = user_result.unwrap()
            if not user:
                return Err("User not found")
            
            user.hashed_password = hashed_password
            user.updated_at = datetime.now(timezone.utc)
            
            self.db.flush()
            return Ok(True)
        except Exception as e:
            logger.error(f"Failed to update password for user {user_id}: {e}")
            self.db.rollback()
            return Err(str(e))
    
    def activate_user(self, user_id: str) -> Result[bool, str]:
        """
        Activate a user account.
        
        Args:
            user_id: User ID
            
        Returns:
            Result containing success boolean or error
        """
        return self._set_user_status(user_id, True)
    
    def deactivate_user(self, user_id: str) -> Result[bool, str]:
        """
        Deactivate a user account.
        
        Args:
            user_id: User ID
            
        Returns:
            Result containing success boolean or error
        """
        return self._set_user_status(user_id, False)
    
    def _set_user_status(
        self, 
        user_id: str, 
        is_active: bool
    ) -> Result[bool, str]:
        """
        Set user's active status.
        
        Args:
            user_id: User ID
            is_active: Active status
            
        Returns:
            Result containing success boolean or error
        """
        try:
            user_result = self.get_by_id(user_id)
            if user_result.is_err():
                return Err(user_result.unwrap_err())
            
            user = user_result.unwrap()
            if not user:
                return Err("User not found")
            
            user.is_active = is_active
            user.updated_at = datetime.now(timezone.utc)
            
            self.db.flush()
            return Ok(True)
        except Exception as e:
            logger.error(f"Failed to set user {user_id} status to {is_active}: {e}")
            self.db.rollback()
            return Err(str(e))
    
    def exists_by_email(self, email: str) -> Result[bool, str]:
        """
        Check if user exists by email.
        
        Args:
            email: User's email address
            
        Returns:
            Result containing existence boolean or error
        """
        try:
            exists = self.db.query(
                self.db.query(User).filter(
                    User.email == email.lower()
                ).exists()
            ).scalar()
            return Ok(exists)
        except Exception as e:
            logger.error(f"Failed to check user existence by email {email}: {e}")
            return Err(str(e))
    
    def count_by_tenant(self, tenant_id: str) -> Result[int, str]:
        """
        Count users in a tenant.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Result containing count or error
        """
        try:
            count = self.db.query(User).filter(
                User.tenant_id == tenant_id
            ).count()
            return Ok(count)
        except Exception as e:
            logger.error(f"Failed to count users in tenant {tenant_id}: {e}")
            return Err(str(e))
    
    def search_users(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> Result[List[User], str]:
        """
        Search users by email or tenant.
        
        Args:
            search_term: Search term
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Result containing list of users or error
        """
        try:
            search_pattern = f"%{search_term}%"
            users = self.db.query(User).filter(
                or_(
                    User.email.ilike(search_pattern),
                    User.tenant_id.ilike(search_pattern)
                )
            ).offset(skip).limit(limit).all()
            return Ok(users)
        except Exception as e:
            logger.error(f"Failed to search users with term '{search_term}': {e}")
            return Err(str(e))