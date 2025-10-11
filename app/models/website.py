from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from ..core.database import Base
from .base import BaseModel

class Website(Base, BaseModel):
    __tablename__ = "websites"
    
    # Basic Info
    website_name = Column(String(100), nullable=False)
    website_url = Column(String(255), nullable=False)
    domain = Column(String(100), index=True)
    description = Column(String(500))
    
    # Configuration
    widget_config = Column(JSON, default=dict)  # position, theme, colors, etc.
    business_hours = Column(JSON, default=dict)  # working hours config
    welcome_message = Column(String(500))
    offline_message = Column(String(500))
    
    # Integration
    embed_code = Column(String(1000))
    api_endpoint = Column(String(255))
    webhook_url = Column(String(255))
    
    # Foreign Keys
    company_id = Column(Integer, ForeignKey("client_companies.id"))
    primary_ai_model_id = Column(Integer, ForeignKey("ai_models.model_id"))
    
    # Relationships
    company = relationship("ClientCompany", back_populates="websites")
    ai_models = relationship("AiModel", back_populates="website", cascade="all, delete-orphan")
    user_access = relationship("UserWebsiteAccess", back_populates="website", cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="website")

