"""
Pydantic models for API request/response validation.
These schemas ensure type safety and data consistency across the application.
"""

from typing import Optional, List
from datetime import date
from pydantic import BaseModel, Field
from decimal import Decimal


class InvoiceData(BaseModel):
    """
    Structured invoice data extracted by AI.
    All fields are optional to handle partial extractions gracefully.
    """
    vendor_name: Optional[str] = Field(None, description="Name of the vendor/supplier")
    invoice_number: Optional[str] = Field(None, description="Invoice number/ID")
    invoice_date: Optional[str] = Field(None, description="Invoice date (YYYY-MM-DD format)")
    subtotal: Optional[float] = Field(None, description="Subtotal amount before tax")
    tax: Optional[float] = Field(None, description="Tax amount")
    total_amount: Optional[float] = Field(None, description="Total amount due")
    currency: Optional[str] = Field(None, description="Currency code (e.g., USD, EUR)")


class ValidationError(BaseModel):
    """
    Individual validation error details.
    """
    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Human-readable error message")
    severity: str = Field(..., description="Error severity: 'error' or 'warning'")


class ValidationResult(BaseModel):
    """
    Validation results for extracted invoice data.
    """
    is_valid: bool = Field(..., description="Whether all validations passed")
    errors: List[ValidationError] = Field(default_factory=list, description="List of validation errors")
    warnings: List[ValidationError] = Field(default_factory=list, description="List of validation warnings")


class InvoiceResponse(BaseModel):
    """
    Complete API response for invoice processing.
    """
    success: bool = Field(..., description="Whether processing completed successfully")
    extracted_data: Optional[InvoiceData] = Field(None, description="Extracted invoice data")
    validation: ValidationResult = Field(..., description="Validation results")
    processing_notes: Optional[str] = Field(None, description="Additional processing information")


class ErrorResponse(BaseModel):
    """
    Standard error response format.
    """
    success: bool = Field(False, description="Always false for errors")
    error_type: str = Field(..., description="Error type identifier")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error details")


# ============================================================================
# Response schemas for GET endpoints
# ============================================================================

class InvoiceListItem(BaseModel):
    """
    Minimal invoice data for list view.
    """
    id: int
    vendor_name: Optional[str]
    invoice_number: Optional[str]
    invoice_date: Optional[str]
    total_amount: Optional[float]
    currency: Optional[str]
    is_valid: bool
    created_at: str  # ISO 8601 format
    
    class Config:
        from_attributes = True


class InvoiceListResponse(BaseModel):
    """
    Response for GET /invoices endpoint.
    """
    count: int = Field(..., description="Total number of invoices")
    invoices: List[InvoiceListItem] = Field(..., description="List of invoices")


class InvoiceDetail(BaseModel):
    """
    Complete invoice data for detail view.
    """
    id: int
    vendor_name: Optional[str]
    invoice_number: Optional[str]
    invoice_date: Optional[str]
    subtotal: Optional[float]
    tax: Optional[float]
    total_amount: Optional[float]
    currency: Optional[str]
    is_valid: bool
    validation_errors: List[str] = Field(default_factory=list)
    created_at: str  # ISO 8601 format
    
    class Config:
        from_attributes = True
