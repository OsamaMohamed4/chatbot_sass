from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base
from .base import BaseModel

class SystemAdmin(Base, BaseModel):
    __tablename__ = "system_admins"
    
    # Basic Info
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    
    # Security
    is_superuser = Column(Boolean, default=False)
    last_login_at = Column(DateTime(timezone=True))
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True))
    
    # 2FA
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(32))
    
    # Relationships
    managed_companies = relationship("ClientCompany", back_populates="managed_by_admin")
    audit_logs = relationship("AuditLog", back_populates="admin")