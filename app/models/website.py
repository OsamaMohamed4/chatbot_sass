from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, JSON, Text
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
    
    # Widget Configuration (individual columns)
    widget_color = Column(String(7), default="#0084ff")  # Hex color
    widget_size = Column(String(20), default="medium")
    widget_position = Column(String(20), default="bottom-right")
    widget_icon = Column(String(255))
    placeholder_text = Column(String(200), default="Type your message...")
    show_powered_by = Column(Boolean, default=True)
    custom_css = Column(Text)
    auto_open_delay = Column(Integer)
    enable_sound = Column(Boolean, default=True)
    enable_file_upload = Column(Boolean, default=False)
    allowed_file_types = Column(JSON, default=list)
    widget_status = Column(String(20), default="active")
    
    # Business Hours
    business_hours_enabled = Column(Boolean, default=False)
    business_hours = Column(JSON, default=dict)
    welcome_message = Column(String(500))
    offline_message = Column(String(500))
    
    # Verification & Security
    domain_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime)
    allowed_domains = Column(JSON, default=list)
    widget_api_key = Column(String(100), unique=True, index=True)
    
    # Analytics
    total_visitors = Column(Integer, default=0)
    total_conversations = Column(Integer, default=0)
    conversion_rate = Column(Integer)
    
    # Integration
    embed_code = Column(Text)
    api_endpoint = Column(String(255))
    webhook_url = Column(String(255))
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Foreign Keys
    company_id = Column(Integer, ForeignKey("client_companies.id"), nullable=False)
    primary_ai_model_id = Column(Integer, ForeignKey("ai_models.model_id"))
    
    # Relationships
    company = relationship("ClientCompany", back_populates="websites")
    ai_models = relationship(
        "AiModel",
        back_populates="website",
        cascade="all, delete-orphan",
        foreign_keys="[AiModel.website_id]"
    )
    primary_ai_model = relationship(
        "AiModel",
        foreign_keys=[primary_ai_model_id],
        post_update=True
    )
    user_access = relationship(
        "UserWebsiteAccess",
        back_populates="website",
        cascade="all, delete-orphan"
    )
    api_keys = relationship(
        "ApiKey",
        back_populates="website",
        cascade="all, delete-orphan"
    )
    chat_sessions = relationship("ChatSession", back_populates="website")
    usage_analytics = relationship("UsageAnalytics", back_populates="website")

