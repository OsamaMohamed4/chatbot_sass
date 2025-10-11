from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from ...core.database import get_db
from ...core.security import security_service
from ...core.config import settings
from ...models.system_admin import SystemAdmin
from ...models.company_user import CompanyUser
from ...schemas.auth import Token, LoginRequest, RefreshTokenRequest

router = APIRouter()

@router.post("/admin/login", response_model=Token)
async def admin_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    # Find admin
    result = await db.execute(
        select(SystemAdmin).where(
            SystemAdmin.username == form_data.username,
            SystemAdmin.is_active == True
        )
    )
    admin = result.scalar_one_or_none()
    
    # Verify credentials
    if not admin or not security_service.verify_password(form_data.password, admin.password_hash):
        # Update failed login attempts
        if admin:
            admin.failed_login_attempts += 1
            if admin.failed_login_attempts >= 5:
                admin.locked_until = datetime.utcnow() + timedelta(minutes=30)
            await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Check if account is locked
    if admin.locked_until and admin.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account is temporarily locked"
        )
    
    # Create tokens
    access_token = security_service.create_access_token(
        subject=admin.id,
        extra_claims={
            "user_type": "admin",
            "is_superuser": admin.is_superuser
        }
    )
    refresh_token = security_service.create_refresh_token(
        subject=admin.id,
        extra_claims={"user_type": "admin"}
    )
    
    # Update login info
    admin.last_login_at = datetime.utcnow()
    admin.failed_login_attempts = 0
    admin.locked_until = None
    await db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/company/login", response_model=Token)
async def company_user_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    # Find user
    result = await db.execute(
        select(CompanyUser).where(
            CompanyUser.username == form_data.username,
            CompanyUser.is_active == True
        )
    )
    user = result.scalar_one_or_none()
    
    # Verify credentials
    if not user or not security_service.verify_password(form_data.password, user.password_hash):
        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=30)
            await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account is temporarily locked"
        )
    
    # Create tokens
    access_token = security_service.create_access_token(
        subject=user.id,
        extra_claims={
            "user_type": "company_user",
            "company_id": user.company_id,
            "role": user.role,
            "is_master": user.is_master_user
        }
    )
    refresh_token = security_service.create_refresh_token(
        subject=user.id,
        extra_claims={
            "user_type": "company_user",
            "company_id": user.company_id
        }
    )
    
    # Update login info
    user.last_login_at = datetime.utcnow()
    user.failed_login_attempts = 0
    user.locked_until = None
    await db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh: RefreshTokenRequest = Body(...)
):
    payload = security_service.decode_token(refresh.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    user_id = payload.get("sub")
    user_type = payload.get("user_type")
    access_token = security_service.create_access_token(
        subject=user_id,
        extra_claims={"user_type": user_type}
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh.refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/logout")
async def logout():
    # Stateless JWT: logout is handled client-side
    return {"message": "Logged out"}


@router.post("/password-reset-request")
async def password_reset_request(
    req: LoginRequest = Body(...)
):
    # TODO: Implement password reset email logic
    return {"message": "Password reset instructions sent if email exists."}