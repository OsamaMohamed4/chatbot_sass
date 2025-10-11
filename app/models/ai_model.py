from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base
from typing import Optional, Dict, Any

# SQLAlchemy Model
class AiModel(Base):
    __tablename__ = "ai_models"

    model_id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey("websites.id"), nullable=False)
    model_name = Column(String(255), nullable=False, index=True)
    model_type = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=False)
    model_config = Column(JSON, default={})
    training_data_config = Column(JSON, default={})
    status = Column(String(50), default="inactive", nullable=False)
    last_trained_at = Column(DateTime)

    # Relationships
    website = relationship("Website", back_populates="ai_models")
    chat_sessions = relationship("ChatSession", back_populates="ai_model")