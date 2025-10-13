from sqlalchemy import Column, DateTime, Integer, Boolean, func
from sqlalchemy.orm import declared_attr
from datetime import datetime



class TimestampMixin:
    """Mixin for adding timestamp fields"""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class BaseModel(TimestampMixin):
    """Base model with common fields"""
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    id = Column(Integer, primary_key=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)