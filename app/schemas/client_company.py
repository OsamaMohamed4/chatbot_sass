from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

class CompanyBase(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=100)
    company_email: EmailStr
    contact_person: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = Field(None, regex="^\\+?[1-9]\\d{1,14}$")
    address: Optional[str] = Field(None, max_length=255)
    industry: Optional[str] = Field(None, max_length=50)
    company_size: Optional[str] = Field(None, regex="^(small|medium|large|enterprise)$")

class CompanyCreate(CompanyBase):
    resource_plan_id: int
    master_user_email: EmailStr
    master_user_firstname: str
    master_user_lastname: str
    master_user_password: Optional[str] = None  # Auto-generate if not provided

class CompanyUpdate(BaseModel):
    company_email: Optional[EmailStr] = None
    contact_person: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, regex="^\\+?[1-9]\\d{1,14}$")
    address: Optional[str] = Field(None, max_length=255)
    industry: Optional[str] = Field(None, max_length=50)
    company_size: Optional[str] = Field(None, regex="^(small|medium|large|enterprise)$")

class CompanyResponse(CompanyBase):
    id: int
    is_active: bool
    account_status: str
    created_at: datetime
    resource_plan: Optional["ResourcePlanResponse"] = None
    resource_allocation: Optional["ResourceAllocationResponse"] = None
    
    class Config:
        from_attributes = True

class ResourcePlanBase(BaseModel):
    plan_name: str = Field(..., min_length=2, max_length=50)
    plan_type: str = Field(..., regex="^(starter|professional|enterprise|custom)$")
    max_ai_models: int = Field(..., ge=1)
    max_users: int = Field(..., ge=1)
    max_websites: int = Field(..., ge=1)
    max_monthly_requests: int = Field(..., ge=100)
    max_storage_gb: Decimal = Field(..., ge=0.1)
    monthly_cost: Decimal = Field(..., ge=0)

class ResourcePlanCreate(ResourcePlanBase):
    features: Optional[Dict[str, bool]] = {}
    max_training_hours: int = Field(10, ge=1)
    overage_cost_per_request: Decimal = Field(0.001, ge=0)
    overage_cost_per_gb: Decimal = Field(0.10, ge=0)

class ResourcePlanResponse(ResourcePlanBase):
    id: int
    features: Dict[str, bool]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ResourceAllocationResponse(BaseModel):
    id: int
    current_ai_models: int
    current_users: int
    current_websites: int
    current_monthly_requests: int
    current_storage_gb: Decimal
    billing_period_start: datetime
    billing_period_end: datetime
    
    class Config:
        from_attributes = True