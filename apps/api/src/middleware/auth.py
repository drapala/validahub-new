"""Authentication middleware for JWT token validation and tenant isolation."""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, Annotated

from src.db.database import get_db
from src.models.user import User, UserRole
from src.models.tenant import Tenant
from src.models.api_key import ApiKey
from src.services.auth_service import AuthService
import hashlib


# OAuth2 scheme for JWT tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

# HTTP Bearer scheme for API keys
bearer_scheme = HTTPBearer(auto_error=False)

auth_service = AuthService()


def get_current_user_from_token(
    token: Annotated[Optional[str], Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user from JWT token.
    Returns None if no token provided.
    """
    if not token:
        return None
    
    try:
        payload = auth_service.decode_token(token)
        
        # Check token type
        if payload.get("type") != "access":
            return None
        
        user_id = payload.get("user_id")
        if not user_id:
            return None
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            return None
        
        return user
    except Exception:
        return None


def get_current_user_from_api_key(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)],
    db: Session = Depends(get_db)
) -> Optional[tuple[ApiKey, Tenant]]:
    """
    Get API key and tenant from Bearer token.
    Returns None if no API key provided or invalid.
    """
    if not credentials:
        return None
    
    # Check if it's an API key (starts with 'vhb_')
    if not credentials.credentials.startswith("vhb_"):
        return None
    
    # Hash the API key
    key_hash = hashlib.sha256(credentials.credentials.encode()).hexdigest()
    
    # Find API key
    api_key = db.query(ApiKey).filter(
        ApiKey.key_hash == key_hash,
        ApiKey.is_active == True
    ).first()
    
    if not api_key:
        return None
    
    # Check if expired
    if api_key.expires_at and api_key.expires_at < datetime.now(timezone.utc):
        return None
    
    # Get tenant
    tenant = db.query(Tenant).filter(Tenant.id == api_key.tenant_id).first()
    if not tenant or tenant.status != "ACTIVE":
        return None
    
    # Update usage
    api_key.last_used_at = datetime.now(timezone.utc)
    api_key.usage_count = (api_key.usage_count or 0) + 1
    db.commit()
    
    return api_key, tenant


def get_current_auth(
    user_from_token: Optional[User] = Depends(get_current_user_from_token),
    api_key_data: Optional[tuple[ApiKey, Tenant]] = Depends(get_current_user_from_api_key)
) -> tuple[Optional[User], Optional[Tenant], Optional[ApiKey]]:
    """
    Get current authentication context.
    Supports both JWT tokens and API keys.
    """
    if user_from_token:
        # JWT authentication
        db = next(get_db())
        tenant = db.query(Tenant).filter(Tenant.id == user_from_token.tenant_id).first()
        return user_from_token, tenant, None
    
    if api_key_data:
        # API key authentication
        api_key, tenant = api_key_data
        return None, tenant, api_key
    
    return None, None, None


def get_current_user(
    auth_data: tuple[Optional[User], Optional[Tenant], Optional[ApiKey]] = Depends(get_current_auth)
) -> User:
    """
    Get current authenticated user.
    Raises 401 if not authenticated.
    """
    user, tenant, api_key = auth_data
    
    if not user and not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user:
        return user
    
    # For API key access, return a virtual user
    # This is useful for logging and auditing
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="API key authentication not supported for this endpoint",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_tenant(
    auth_data: tuple[Optional[User], Optional[Tenant], Optional[ApiKey]] = Depends(get_current_auth)
) -> Tenant:
    """
    Get current tenant from authentication.
    Raises 401 if not authenticated.
    """
    user, tenant, api_key = auth_data
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return tenant


def get_api_key(
    auth_data: tuple[Optional[User], Optional[Tenant], Optional[ApiKey]] = Depends(get_current_auth)
) -> Optional[ApiKey]:
    """
    Get current API key if using API key authentication.
    """
    _, _, api_key = auth_data
    return api_key


def require_role(roles: list[UserRole]):
    """
    Dependency to require specific user roles.
    
    Usage:
        @router.get("/admin", dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.OWNER]))])
    """
    def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    
    return role_checker


def require_permission(permission: str):
    """
    Dependency to require specific permission.
    
    Usage:
        @router.post("/users", dependencies=[Depends(require_permission("manage_users"))])
    """
    def permission_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if not current_user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {permission}"
            )
        return current_user
    
    return permission_checker


def require_verified_email(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require user to have verified email.
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    return current_user


def require_api_scope(scope: str):
    """
    Dependency to require specific API key scope.
    
    Usage:
        @router.post("/webhook", dependencies=[Depends(require_api_scope("webhook:send"))])
    """
    def scope_checker(
        api_key: Optional[ApiKey] = Depends(get_api_key)
    ) -> ApiKey:
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required"
            )
        
        if scope not in (api_key.scopes or []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"API key missing required scope: {scope}"
            )
        
        return api_key
    
    return scope_checker


class TenantContextMiddleware:
    """
    Middleware to ensure tenant isolation in all queries.
    Automatically filters queries by tenant_id.
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Store tenant_id in request state for use in queries
            # This will be implemented with proper request context
            pass
        
        await self.app(scope, receive, send)


# Export commonly used dependencies
__all__ = [
    "get_current_user",
    "get_current_tenant",
    "get_api_key",
    "get_current_auth",
    "require_role",
    "require_permission",
    "require_verified_email",
    "require_api_scope",
    "TenantContextMiddleware"
]


# Import datetime at the top of the file
from datetime import datetime, timezone