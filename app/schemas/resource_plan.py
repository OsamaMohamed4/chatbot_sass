from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import relationship
from ..core.database import Base
from .base import BaseModel, Field
from typing import Optional
from decimal import Decimal


class ResourcePlanBase(BaseModel):
    plan_name: str
    max_ai_models: int = Field(gt=0)
    max_users: int = Field(gt=0)
    max_monthly_requests: int = Field(gt=0)
    max_storage_gb: Decimal = Field(gt=0)
    monthly_cost: Decimal = Field(ge=0)

class ResourcePlanCreate(ResourcePlanBase):
    pass

class ResourcePlanUpdate(BaseModel):
    plan_name: Optional[str] = None
    max_ai_models: Optional[int] = Field(None, gt=0)
    max_users: Optional[int] = Field(None, gt=0)
    max_monthly_requests: Optional[int] = Field(None, gt=0)
    max_storage_gb: Optional[Decimal] = Field(None, gt=0)
    monthly_cost: Optional[Decimal] = Field(None, ge=0)

class ResourcePlanResponse(ResourcePlanBase):
    plan_id: int

    class Config:
        from_attributes = True
