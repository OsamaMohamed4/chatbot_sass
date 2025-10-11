from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, JSON, Numeric
from sqlalchemy.orm import relationship
from ..core.database import Base
from .base import BaseModel



class ResourceAllocation(Base, BaseModel):
    __tablename__ = "resource_allocations"
    
    # Foreign Keys
    company_id = Column(Integer, ForeignKey("client_companies.id"), unique=True)
    plan_id = Column(Integer, ForeignKey("resource_plans.id"))
    
    # Current Usage
    current_ai_models = Column(Integer, default=0)
    current_users = Column(Integer, default=0)
    current_websites = Column(Integer, default=0)
    current_monthly_requests = Column(Integer, default=0)
    current_storage_gb = Column(Numeric(10, 2), default=0)
    
    # Billing Period
    billing_period_start = Column(DateTime(timezone=True))
    billing_period_end = Column(DateTime(timezone=True))
    
    # Overage Tracking
    overage_requests = Column(Integer, default=0)
    overage_storage_gb = Column(Numeric(10, 2), default=0)
    
    # Relationships
    company = relationship("ClientCompany", back_populates="resource_allocation")
    plan = relationship("ResourcePlan", back_populates="allocations")