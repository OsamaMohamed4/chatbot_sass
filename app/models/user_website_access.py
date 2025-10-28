from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from ..core.database import Base
from .base import BaseModel

class UserWebsiteAccess(Base, BaseModel):
    __tablename__ = "user_website_access"
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("company_users.id"))
    website_id = Column(Integer, ForeignKey("websites.id"))
    
    # Permissions
    permission_level = Column(String(20), nullable=False)  # full, read, write, limited
    custom_permissions = Column(JSON, default=dict)
    
    # Access Period
    granted_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    granted_by_id = Column(Integer, ForeignKey("company_users.id"))
    
    # Fixed Relationships
    user = relationship("CompanyUser", back_populates="website_access", foreign_keys=[user_id])
    website = relationship("Website", back_populates="user_access")
    granted_by = relationship("CompanyUser", foreign_keys=[granted_by_id])