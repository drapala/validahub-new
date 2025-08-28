"""Authentication service for JWT token management."""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
import secrets
import os

from src.models.user import User, UserRole
from src.models.tenant import Tenant


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7


class AuthService:
    """Service for authentication and JWT token management."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password for storing."""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(
        user_id: str,
        tenant_id: str,
        email: str,
        role: UserRole,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token."""
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        payload = {
            "sub": user_id,  # Subject (user ID)
            "tenant_id": tenant_id,
            "email": email,
            "role": role.value,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access"
        }
        
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def create_refresh_token(
        user_id: str,
        tenant_id: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT refresh token."""
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        payload = {
            "sub": user_id,
            "tenant_id": tenant_id,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh",
            "jti": secrets.token_urlsafe(32)  # JWT ID for revocation
        }
        
        return jwt.encode(payload, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def decode_access_token(token: str) -> Dict[str, Any]:
        """Decode and validate an access token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Verify it's an access token
            if payload.get("type") != "access":
                raise jwt.InvalidTokenError("Invalid token type")
            
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {str(e)}")
    
    @staticmethod
    def decode_refresh_token(token: str) -> Dict[str, Any]:
        """Decode and validate a refresh token."""
        try:
            payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
            
            # Verify it's a refresh token
            if payload.get("type") != "refresh":
                raise jwt.InvalidTokenError("Invalid token type")
            
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Refresh token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid refresh token: {str(e)}")
    
    @staticmethod
    def create_token_pair(user: User) -> Dict[str, str]:
        """Create both access and refresh tokens for a user."""
        access_token = AuthService.create_access_token(
            user_id=user.id,
            tenant_id=user.tenant_id,
            email=user.email,
            role=user.role
        )
        
        refresh_token = AuthService.create_refresh_token(
            user_id=user.id,
            tenant_id=user.tenant_id
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # in seconds
        }
    
    @staticmethod
    def create_password_reset_token(user_id: str, email: str) -> str:
        """Create a password reset token."""
        expire = datetime.now(timezone.utc) + timedelta(hours=1)
        
        payload = {
            "sub": user_id,
            "email": email,
            "exp": expire,
            "type": "password_reset"
        }
        
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def verify_password_reset_token(token: str) -> Dict[str, Any]:
        """Verify a password reset token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            if payload.get("type") != "password_reset":
                raise jwt.InvalidTokenError("Invalid token type")
            
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Password reset token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid password reset token: {str(e)}")
    
    @staticmethod
    def create_email_verification_token(user_id: str, email: str) -> str:
        """Create an email verification token."""
        expire = datetime.now(timezone.utc) + timedelta(days=7)
        
        payload = {
            "sub": user_id,
            "email": email,
            "exp": expire,
            "type": "email_verification"
        }
        
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def verify_email_verification_token(token: str) -> Dict[str, Any]:
        """Verify an email verification token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            if payload.get("type") != "email_verification":
                raise jwt.InvalidTokenError("Invalid token type")
            
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Email verification token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid email verification token: {str(e)}")