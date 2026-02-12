"""
SQLAlchemy ORM models for database tables.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class Invoice(Base):
    """
    Invoice table for storing processed invoice data.
    
    Phase 1: Added status field for workflow management.
    """
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    vendor_name = Column(String(255), nullable=True)
    invoice_number = Column(String(100), nullable=True, index=True)
    invoice_date = Column(String(50), nullable=True)
    subtotal = Column(Float, nullable=True)
    tax = Column(Float, nullable=True)
    total_amount = Column(Float, nullable=True)
    currency = Column(String(10), nullable=True)
    is_valid = Column(Boolean, default=False, nullable=False)
    validation_errors = Column(Text, nullable=True)  # JSON string of errors AND warnings
    
    # Phase 1: Status field for processing workflow
    # Values: "PENDING", "REVIEW_REQUIRED", "APPROVED"
    status = Column(String(50), default="PENDING", nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Invoice(id={self.id}, invoice_number={self.invoice_number}, vendor={self.vendor_name})>"
