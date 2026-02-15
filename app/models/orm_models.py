"""
SQLAlchemy ORM models for invoice storage.
Maps to the 'invoices' table in the PostgreSQL database.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class User(Base):
    """
    User model linked to Supabase Auth.
    
    Stores local user data with UUID matching Supabase user ID.
    Enables foreign key relationships for multi-user invoice ownership.
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationship to invoices
    invoices = relationship("Invoice", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class Invoice(Base):
    """
    ORM model for stored invoices.

    Stores extracted invoice data including line items (as JSON),
    discount details, tax breakdown (CGST/SGST), and approval status.
    Each invoice belongs to a user (multi-user support).
    """
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    vendor_name = Column(String(200), nullable=True)
    invoice_number = Column(String(100), nullable=True, index=True)
    invoice_date = Column(String(50), nullable=True)

    # Line items stored as JSON text
    line_items = Column(Text, nullable=True)

    # Subtotal (sum of line item amounts)
    subtotal = Column(Float, nullable=True)

    # Discount
    discount_percentage = Column(Float, nullable=True)
    discount_amount = Column(Float, nullable=True)

    # Tax breakdown (Indian GST)
    cgst_rate = Column(Float, nullable=True)
    cgst_amount = Column(Float, nullable=True)
    sgst_rate = Column(Float, nullable=True)
    sgst_amount = Column(Float, nullable=True)

    # Total tax (sum of CGST + SGST or legacy single value)
    tax = Column(Float, nullable=True)

    # Grand total
    total_amount = Column(Float, nullable=True)

    currency = Column(String(10), nullable=True)
    is_valid = Column(Boolean, default=False, nullable=False)
    validation_errors = Column(Text, nullable=True)

    # Approval workflow
    status = Column(String(50), default="PENDING", nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationship to user
    user = relationship("User", back_populates="invoices")

    def __repr__(self):
        return f"<Invoice(id={self.id}, invoice_number={self.invoice_number}, vendor={self.vendor_name}, user_id={self.user_id})>"
