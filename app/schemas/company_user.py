
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base
from .base import BaseModel, EmailStr
from typing import Optional



class CompanyUserBase(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    role: str
    is_master_user: bool = False

class CompanyUserCreate(CompanyUserBase):
    company_id: int
    password: str
    parent_user_id: Optional[int] = None

class CompanyUserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    last_login_at: Optional[datetime] = None

class CompanyUserResponse(CompanyUserBase):
    user_id: int
    company_id: int
    parent_user_id: Optional[int] = None
    created_at: datetime
    last_login_at: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True