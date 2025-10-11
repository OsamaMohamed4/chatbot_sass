from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class AdminBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)

class AdminCreate(AdminBase):
    password: str = Field(..., min_length=8)
    is_superuser: bool = False

class AdminUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    is_active: Optional[bool] = None

class AdminResponse(AdminBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    last_login_at: Optional[datetime]
    
    class Config:
        from_attributes = True