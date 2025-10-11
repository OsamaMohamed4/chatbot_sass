from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, JSON
from sqlalchemy.orm import relationship
from ..core.database import Base
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import date

# SQLAlchemy Model
class BillingRecord(Base):
    __tablename__ = "billing_records"

    billing_id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("client_companies.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    billing_period = Column(String(50), nullable=False)
    billing_date = Column(Date, nullable=False, index=True)
    status = Column(String(50), default="pending", nullable=False)
    usage_details = Column(JSON, default={})

    # Relationships
    client_company = relationship("ClientCompany", back_populates="billing_records")