from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, status, HTTPException
from pydantic import BaseModel, EmailStr, Field

from app.api.dependencies import PaginationDep, DatabaseDep
from app.api.deps import AuthDependencies
from app.services.user_service import UserService
from app.schemas.responses import (
    SuccessResponse,
    PaginatedResponse,
    MessageResponse,
    success_response,
    paginated_response
)
from app.models.company_user import CompanyUser

router = APIRouter()
auth_deps = AuthDependencies()


# ========================
# Schemas
# ========================

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    role: str = Field(..., pattern=r"^(admin|operator|viewer)$")
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    role: Optional[str] = Field(None, pattern=r"^(admin|operator|viewer)$")
    password: Optional[str] = Field(None, min_length=8)


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    role: str
    is_master_user: bool
    is_active: bool
    company_id: Optional[int] = None
    last_login_at: Optional[datetime] = None
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }


# ========================
# Dependency
# ========================

def get_user_service(db: DatabaseDep) -> UserService:
    return UserService(db)


# ========================
# Endpoints
# ========================

@router.post(
    "",
    response_model=SuccessResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create new user",
    description="Create new user (master only)"
)
async def create_user(
    user_data: UserCreate,
    db: DatabaseDep,
    current_user: CompanyUser = Depends(auth_deps.require_master_user)
):
    """Create new user (master only)"""
    service = UserService(db)
    user = await service.create_user(
        user_data.model_dump(),
        current_user.company_id,
        current_user.id
    )
    return success_response(
        data=UserResponse.model_validate(user),
        message="User created successfully"
    )


@router.get(
    "",
    response_model=PaginatedResponse[UserResponse],
    summary="List users",
    description="Get all users in the company"
)
async def list_users(
    db: DatabaseDep,
    pagination: PaginationDep,
    role: Optional[str] = Query(None, description="Filter by role"),
    current_user: CompanyUser = Depends(auth_deps.get_current_company_user)
):
    """List company users"""
    service = UserService(db)
    
    if role:
        users = await service.get_users_by_role(
            current_user.company_id, role,
            pagination["skip"], pagination["limit"]
        )
        total = len(users)
    else:
        users, total = await service.get_company_users(
            current_user.company_id,
            pagination["skip"],
            pagination["limit"]
        )
    
    return paginated_response(
        data=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=pagination["page"],
        page_size=pagination["page_size"]
    )


@router.get(
    "/{user_id}",
    response_model=SuccessResponse[UserResponse],
    summary="Get user details",
    description="Get detailed information about a user"
)
async def get_user(
    user_id: int,
    db: DatabaseDep,
    current_user: CompanyUser = Depends(auth_deps.get_current_company_user)
):
    """Get user details"""
    service = UserService(db)
    user = await service.get_user(user_id)
    
    # Check if user belongs to same company
    if user.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this user"
        )
    
    return success_response(data=UserResponse.model_validate(user))


@router.put(
    "/{user_id}",
    response_model=SuccessResponse[UserResponse],
    summary="Update user",
    description="Update user information"
)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: DatabaseDep,
    current_user: CompanyUser = Depends(auth_deps.get_current_company_user)
):
    """Update user"""
    service = UserService(db)
    
    # Check if user belongs to same company
    user = await service.get_user(user_id)
    if user.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this user"
        )
    
    updated_user = await service.update_user(
        user_id,
        user_data.model_dump(exclude_unset=True),
        current_user.id
    )
    
    return success_response(
        data=UserResponse.model_validate(updated_user),
        message="User updated successfully"
    )


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    summary="Delete user",
    description="Soft delete a user (master only)"
)
async def delete_user(
    user_id: int,
    db: DatabaseDep,
    current_user: CompanyUser = Depends(auth_deps.require_master_user)
):
    """Delete user (master only)"""
    service = UserService(db)
    
    # Check if user belongs to same company
    user = await service.get_user(user_id)
    if user.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this user"
        )
    
    # Prevent deleting master user
    if user.is_master_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete master user"
        )
    
    await service.delete_user(user_id, current_user.id)
    return {
        "success": True,
        "message": "User deleted successfully"
    }