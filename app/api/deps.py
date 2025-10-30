from typing import Optional, Annotated, Union
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt
from ..core.database import get_db
from ..core.config import settings
from ..core.security import security_service
from ..models.system_admin import SystemAdmin
from ..models.company_user import CompanyUser
from ..models.client_company import ClientCompany

security = HTTPBearer()

# ==========================================
# Token Validation (NOT async - no DB call)
# ==========================================
def get_current_token(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    """Decode and return token payload"""
    token = credentials.credentials
    payload = security_service.decode_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


# ==========================================
# Get Current Admin (async - DB call)
# ==========================================
async def get_current_admin(
    token_data: dict = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
) -> SystemAdmin:
    """Get current admin from token"""
    if token_data.get("user_type") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    admin_id = int(token_data.get("sub"))
    result = await db.execute(
        select(SystemAdmin).where(
            SystemAdmin.id == admin_id,
            SystemAdmin.is_active == True
        )
    )
    admin = result.scalar_one_or_none()
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )
    
    return admin


# ==========================================
# Get Current Company User (async - DB call)
# ==========================================
async def get_current_company_user(
    token_data: dict = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
) -> CompanyUser:
    """Get current company user from token"""
    if token_data.get("user_type") != "company_user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user_id = int(token_data.get("sub"))
    result = await db.execute(
        select(CompanyUser).where(
            CompanyUser.id == user_id,
            CompanyUser.is_active == True
        )
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


# ==========================================
# Get Current Active User (Admin or Company User)
# ==========================================
async def get_current_active_user(
    token_data: dict = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
) -> Union[SystemAdmin, CompanyUser]:
    """Get current user (admin or company user)"""
    user_type = token_data.get("user_type")
    
    if user_type == "admin":
        return await get_current_admin(token_data, db)
    elif user_type == "company_user":
        return await get_current_company_user(token_data, db)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid user type"
        )


# ==========================================
# Require Superuser (async)
# ==========================================
async def require_superuser(
    current_admin: SystemAdmin = Depends(get_current_admin)
) -> SystemAdmin:
    """Require superuser privileges"""
    if not current_admin.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser access required"
        )
    return current_admin


# ==========================================
# Require Master User (async)
# ==========================================
async def require_master_user(
    current_user: CompanyUser = Depends(get_current_company_user)
) -> CompanyUser:
    """Require master user privileges"""
    if not current_user.is_master_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Master user access required"
        )
    return current_user


# ==========================================
# Legacy Support (for old code using auth_deps)
# ==========================================
class AuthDependencies:
    """Legacy class for backward compatibility"""
    get_current_token = staticmethod(get_current_token)
    get_current_admin = staticmethod(get_current_admin)
    get_current_company_user = staticmethod(get_current_company_user)
    get_current_active_user = staticmethod(get_current_active_user)
    require_superuser = staticmethod(require_superuser)
    require_master_user = staticmethod(require_master_user)

auth_deps = AuthDependencies()