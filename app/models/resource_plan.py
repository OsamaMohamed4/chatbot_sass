from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, JSON, Numeric
from sqlalchemy.orm import relationship
from ..core.database import Base
from .base import BaseModel




class ResourcePlan(Base, BaseModel):
    __tablename__ = "resource_plans"
    
    # Plan Details
    plan_name = Column(String(50), unique=True, nullable=False)
    plan_type = Column(String(20), nullable=False)  # starter, professional, enterprise
    
    # Resource Limits
    max_ai_models = Column(Integer, nullable=False)
    max_users = Column(Integer, nullable=False)
    max_websites = Column(Integer, nullable=False)
    max_monthly_requests = Column(Integer, nullable=False)
    max_storage_gb = Column(Numeric(10, 2), nullable=False)
    max_training_hours = Column(Integer, default=10)
    
    # Pricing
    monthly_cost = Column(Numeric(10, 2), nullable=False)
    yearly_cost = Column(Numeric(10, 2))
    overage_cost_per_request = Column(Numeric(10, 4), default=0.001)
    overage_cost_per_gb = Column(Numeric(10, 2), default=0.10)
    
    # Features
    features = Column(JSON, default=dict)  # {feature_name: enabled}
    
    # Relationships
    companies = relationship("ClientCompany", back_populates="resource_plan")
    allocations = relationship("ResourceAllocation", back_populates="plan")