"""Authentication endpoints for multi-tenant system."""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from src.db.database import get_db
from src.models.tenant import Tenant, TenantPlan, TenantStatus
from src.models.user import User, UserRole
from src.services.auth_service import AuthService
from src.middleware.auth import get_current_user, get_current_tenant
import uuid
import secrets


router = APIRouter(prefix="/auth", tags=["authentication"])
auth_service = AuthService()


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str
    tenant_slug: Optional[str] = Field(None, description="Tenant slug for multi-tenant login")


class RegisterRequest(BaseModel):
    """Registration request for new tenant and owner."""
    # Company info
    company_name: str = Field(..., min_length=2, max_length=100)
    company_slug: str = Field(..., min_length=2, max_length=50, pattern="^[a-z0-9-]+$")
    company_email: EmailStr
    company_cnpj: Optional[str] = Field(None, max_length=20)
    
    # Owner info
    owner_name: str = Field(..., min_length=2, max_length=100)
    owner_email: EmailStr
    owner_password: str = Field(..., min_length=8, max_length=100)
    owner_phone: Optional[str] = Field(None, max_length=20)


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    user: dict
    tenant: dict


class RefreshRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Password reset request."""
    email: EmailStr
    tenant_slug: str


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation."""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class VerifyEmailRequest(BaseModel):
    """Email verification request."""
    token: str


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT tokens.
    
    For multi-tenant systems, provide tenant_slug to identify the tenant.
    """
    # Find user by email
    query = db.query(User).filter(User.email == request.email)
    
    # If tenant_slug provided, filter by tenant
    if request.tenant_slug:
        tenant = db.query(Tenant).filter(Tenant.slug == request.tenant_slug).first()
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        query = query.filter(User.tenant_id == tenant.id)
    
    user = query.first()
    
    if not user or not auth_service.verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Check if user is locked
    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is temporarily locked due to multiple failed login attempts"
        )
    
    # Get tenant
    tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Check tenant status
    if tenant.status == TenantStatus.SUSPENDED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant account is suspended"
        )
    
    # Generate tokens
    access_token = auth_service.create_access_token(
        user_id=user.id,
        tenant_id=user.tenant_id,
        email=user.email,
        role=user.role
    )
    
    refresh_token = auth_service.create_refresh_token(
        user_id=user.id,
        tenant_id=user.tenant_id
    )
    
    # Update user's last login and store refresh token
    user.last_login = datetime.now(timezone.utc)
    user.failed_login_attempts = 0
    user.locked_until = None
    user.refresh_token = refresh_token
    db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=3600,
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role.value,
            "is_verified": user.is_verified,
            "avatar_url": user.avatar_url
        },
        tenant={
            "id": tenant.id,
            "name": tenant.name,
            "slug": tenant.slug,
            "plan": tenant.plan.value,
            "features": tenant.features
        }
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new tenant with an owner user.
    
    This creates:
    1. A new tenant account with FREE plan
    2. An owner user for the tenant
    3. Returns JWT tokens for immediate login
    """
    # Check if tenant slug already exists
    existing_tenant = db.query(Tenant).filter(Tenant.slug == request.company_slug).first()
    if existing_tenant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company slug already taken"
        )
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.owner_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new tenant
    tenant = Tenant(
        id=f"tenant_{uuid.uuid4().hex[:12]}",
        name=request.company_name,
        slug=request.company_slug,
        company_name=request.company_name,
        cnpj=request.company_cnpj,
        email=request.company_email,
        plan=TenantPlan.FREE,
        status=TenantStatus.TRIAL,
        max_users=3,
        max_validations_per_month=100,
        max_file_size_mb=10,
        features={
            "bulk_upload": False,
            "api_access": False,
            "custom_rules": False,
            "white_label": False,
            "priority_support": False,
            "data_export": True,
            "webhooks": False,
            "sso": False
        },
        settings={
            "theme": "light",
            "notifications": {
                "email": True,
                "webhook": False
            },
            "security": {
                "require_mfa": False,
                "password_policy": "standard"
            }
        },
        is_verified=False
    )
    db.add(tenant)
    
    # Create owner user
    user = User(
        id=f"user_{uuid.uuid4().hex[:12]}",
        tenant_id=tenant.id,
        email=request.owner_email,
        hashed_password=auth_service.hash_password(request.owner_password),
        name=request.owner_name,
        phone=request.owner_phone,
        role=UserRole.OWNER,
        is_active=True,
        is_verified=False,
        email_verification_token=secrets.token_urlsafe(32),
        last_login=datetime.now(timezone.utc)
    )
    db.add(user)
    
    # Commit to database
    db.commit()
    db.refresh(tenant)
    db.refresh(user)
    
    # Generate tokens for immediate login
    access_token = auth_service.create_access_token(
        user_id=user.id,
        tenant_id=tenant.id,
        email=user.email,
        role=user.role
    )
    
    refresh_token = auth_service.create_refresh_token(
        user_id=user.id,
        tenant_id=tenant.id
    )
    
    # Store refresh token
    user.refresh_token = refresh_token
    db.commit()
    
    # TODO: Send verification email
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=3600,
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role.value,
            "is_verified": user.is_verified,
            "avatar_url": user.avatar_url
        },
        tenant={
            "id": tenant.id,
            "name": tenant.name,
            "slug": tenant.slug,
            "plan": tenant.plan.value,
            "features": tenant.features
        }
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    """
    # Decode refresh token
    try:
        payload = auth_service.decode_token(request.refresh_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Check if it's a refresh token
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    # Find user
    user = db.query(User).filter(User.id == payload.get("user_id")).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify stored refresh token matches
    if user.refresh_token != request.refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Get tenant
    tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Generate new tokens
    new_access_token = auth_service.create_access_token(
        user_id=user.id,
        tenant_id=user.tenant_id,
        email=user.email,
        role=user.role
    )
    
    new_refresh_token = auth_service.create_refresh_token(
        user_id=user.id,
        tenant_id=user.tenant_id
    )
    
    # Update refresh token
    user.refresh_token = new_refresh_token
    db.commit()
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        expires_in=3600,
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role.value,
            "is_verified": user.is_verified,
            "avatar_url": user.avatar_url
        },
        tenant={
            "id": tenant.id,
            "name": tenant.name,
            "slug": tenant.slug,
            "plan": tenant.plan.value,
            "features": tenant.features
        }
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout current user by invalidating refresh token.
    """
    user = db.query(User).filter(User.id == current_user.id).first()
    if user:
        user.refresh_token = None
        db.commit()
    
    return {"message": "Successfully logged out"}


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Get current user and tenant information.
    """
    return {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "role": current_user.role.value,
            "department": current_user.department,
            "is_verified": current_user.is_verified,
            "is_active": current_user.is_active,
            "avatar_url": current_user.avatar_url,
            "two_factor_enabled": current_user.two_factor_enabled,
            "preferences": current_user.preferences
        },
        "tenant": {
            "id": current_tenant.id,
            "name": current_tenant.name,
            "slug": current_tenant.slug,
            "plan": current_tenant.plan.value,
            "status": current_tenant.status.value,
            "features": current_tenant.features,
            "limits": {
                "max_users": current_tenant.max_users,
                "max_validations_per_month": current_tenant.max_validations_per_month,
                "max_file_size_mb": current_tenant.max_file_size_mb
            }
        }
    }


@router.post("/password-reset/request")
async def request_password_reset(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request a password reset token.
    """
    # Find tenant
    tenant = db.query(Tenant).filter(Tenant.slug == request.tenant_slug).first()
    if not tenant:
        # Don't reveal if tenant doesn't exist
        return {"message": "If the email exists, a reset link has been sent"}
    
    # Find user
    user = db.query(User).filter(
        User.email == request.email,
        User.tenant_id == tenant.id
    ).first()
    
    if user:
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        user.password_reset_token = reset_token
        user.password_reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        db.commit()
        
        # TODO: Send password reset email
    
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/password-reset/confirm")
async def confirm_password_reset(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Confirm password reset with token.
    """
    # Find user by reset token
    user = db.query(User).filter(
        User.password_reset_token == request.token
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Check if token is expired
    if user.password_reset_expires < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired"
        )
    
    # Update password
    user.hashed_password = auth_service.hash_password(request.new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    db.commit()
    
    return {"message": "Password successfully reset"}


@router.post("/verify-email")
async def verify_email(
    request: VerifyEmailRequest,
    db: Session = Depends(get_db)
):
    """
    Verify user email with token.
    """
    # Find user by verification token
    user = db.query(User).filter(
        User.email_verification_token == request.token
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    # Mark as verified
    user.is_verified = True
    user.email_verification_token = None
    db.commit()
    
    return {"message": "Email successfully verified"}