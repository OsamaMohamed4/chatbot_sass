from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base

class ApiKey(Base):
    __tablename__ = "api_keys"

    key_id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey("websites.id"), nullable=False)
    key_name = Column(String(255), nullable=False)
    api_key_hash = Column(String(255), unique=True, nullable=False, index=True)
    permissions = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime)
    last_used_at = Column(DateTime)
    is_active = Column(Boolean, default=True, nullable=False)

    # Fixed Relationships
    website = relationship("Website", back_populates="api_keys")