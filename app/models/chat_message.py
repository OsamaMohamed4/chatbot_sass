from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Text, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    message_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.session_id"), nullable=False)
    message_type = Column(String(50), nullable=False)
    message_content = Column(Text, nullable=False)
    message_metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    response_time_ms = Column(Integer)
    tokens_used = Column(Numeric(10, 2))
    is_user_message = Column(Boolean, nullable=False)

    # Fixed Relationships
    chat_session = relationship("ChatSession", back_populates="chat_messages")