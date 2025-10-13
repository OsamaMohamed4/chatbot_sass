from sqlalchemy import Column, Integer, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base
from typing import Optional
from decimal import Decimal
from datetime import date

# SQLAlchemy Model
class UsageAnalytics(Base):
    __tablename__ = "usage_analytics"

    analytics_id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("client_companies.id"), nullable=False)
    website_id = Column(Integer, ForeignKey("websites.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("company_users.id"), nullable=True)
    usage_date = Column(Date, nullable=False, index=True)
    total_requests = Column(Integer, default=0, nullable=False)
    total_tokens_used = Column(Numeric(15, 2), default=0, nullable=False)
    total_sessions = Column(Integer, default=0, nullable=False)
    avg_response_time_ms = Column(Numeric(10, 2), default=0, nullable=False)

    # Relationships
    client_company = relationship("ClientCompany", back_populates="usage_analytics")
    website = relationship("Website", back_populates="usage_analytics")
    company_user = relationship("CompanyUser", back_populates="usage_analytics")