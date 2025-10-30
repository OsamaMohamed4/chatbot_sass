
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class CompanyUserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    role: str = Field(..., pattern=r"^(admin|operator|viewer)$")


class CompanyUserCreate(CompanyUserBase):
    password: str = Field(..., min_length=8)


class CompanyUserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    role: Optional[str] = Field(None, pattern=r"^(admin|operator|viewer)$")
    password: Optional[str] = Field(None, min_length=8)


class CompanyUserResponse(CompanyUserBase):
    id: int
    company_id: int
    is_master_user: bool
    is_active: bool
    created_by_id: Optional[int] = None
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {
        "from_attributes": True
    }