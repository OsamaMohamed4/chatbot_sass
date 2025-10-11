from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from ..core.database import Base
from .base import BaseModel

class CompanyUser(Base, BaseModel):
    __tablename__ = "company_users"
    
    # Basic Info
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    
    # Role & Permissions
    role = Column(String(20), nullable=False)  # master, admin, operator, viewer
    is_master_user = Column(Boolean, default=False)
    custom_permissions = Column(JSON, default=dict)
    
    # Account Info
    last_login_at = Column(DateTime(timezone=True))
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True))
    password_changed_at = Column(DateTime(timezone=True))
    
    # Foreign Keys
    company_id = Column(Integer, ForeignKey("client_companies.id"))
    created_by_id = Column(Integer, ForeignKey("company_users.id"))
    
    # Relationships
    company = relationship("ClientCompany", back_populates="users")
    created_by = relationship("CompanyUser", remote_side="CompanyUser.id")
    website_access = relationship("UserWebsiteAccess", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user")