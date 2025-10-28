from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    session_id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey("websites.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("company_users.id"), nullable=False)
    model_id = Column(Integer, ForeignKey("ai_models.model_id"), nullable=False)
    session_name = Column(String(255))
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime)
    is_active = Column(Boolean, default=True, nullable=False)
    session_metadata = Column(JSON, default={})

    # Fixed Relationships
    website = relationship("Website", back_populates="chat_sessions")
    company_user = relationship("CompanyUser", back_populates="chat_sessions")
    ai_model = relationship("AiModel", back_populates="chat_sessions")
    chat_messages = relationship("ChatMessage", back_populates="chat_session", cascade="all, delete-orphan")