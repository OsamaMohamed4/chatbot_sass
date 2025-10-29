from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, JSON, Numeric
from sqlalchemy.orm import relationship
from ..core.database import Base
from .base import BaseModel

class ClientCompany(Base, BaseModel):
    __tablename__ = "client_companies"
    
    # Basic Info
    company_name = Column(String(100), unique=True, nullable=False)
    company_email = Column(String(100), unique=True, nullable=False)
    contact_person = Column(String(100), nullable=False)
    phone = Column(String(20))
    address = Column(String(255))
    
    # Business Info
    industry = Column(String(50))
    company_size = Column(String(20))
    tax_id = Column(String(50))
    
    # Account Info
    account_status = Column(String(20), default="active")
    suspension_reason = Column(String(255))
    
    # Relationships
    admin_id = Column(Integer, ForeignKey("system_admins.id"))
    resource_plan_id = Column(Integer, ForeignKey("resource_plans.id"))
    
    # Fixed Relationships
    managed_by_admin = relationship("SystemAdmin", back_populates="managed_companies")
    resource_plan = relationship("ResourcePlan", back_populates="companies")
    resource_allocation = relationship(
        "ResourceAllocation",
        back_populates="company",
        uselist=False
    )
    websites = relationship(
        "Website",
        back_populates="company",
        cascade="all, delete-orphan"
    )
    users = relationship(
        "CompanyUser",
        back_populates="company",
        cascade="all, delete-orphan"
    )
    billing_records = relationship("BillingRecord", back_populates="company")
    usage_analytics = relationship("UsageAnalytics", back_populates="client_company")