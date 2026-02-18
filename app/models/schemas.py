"""
Pydantic models for API request/response validation.
These schemas ensure type safety and data consistency across the application.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Line Item model
# ---------------------------------------------------------------------------
class LineItem(BaseModel):
    """
    A single product/service line item on an invoice.

    The amount should equal quantity × unit_price.
    """
    product_name: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    amount: Optional[float] = None


# ---------------------------------------------------------------------------
# Invoice Data (extraction output)
# ---------------------------------------------------------------------------
class InvoiceData(BaseModel):
    """
    Structured invoice data returned by the extraction service.

    Represents the complete extracted invoice with line items,
    discount, tax breakdown, and totals.
    """
    vendor_name: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None

    # Line items
    line_items: List[LineItem] = Field(default_factory=list)

    # Subtotal (sum of all line item amounts)
    subtotal: Optional[float] = None

    # Discount
    discount_percentage: Optional[float] = None
    discount_amount: Optional[float] = None

    # Tax breakdown (Indian GST)
    cgst_rate: Optional[float] = None
    cgst_amount: Optional[float] = None
    sgst_rate: Optional[float] = None
    sgst_amount: Optional[float] = None
    tax: Optional[float] = None  # Total tax (CGST + SGST or legacy single tax)

    # Grand total
    total_amount: Optional[float] = None
    currency: Optional[str] = None


# ---------------------------------------------------------------------------
# Validation models
# ---------------------------------------------------------------------------
class ValidationError(BaseModel):
    """A single validation issue (error or warning)."""
    field: str
    message: str
    severity: str  # "error" or "warning"


class ValidationResult(BaseModel):
    """Aggregated validation results for an invoice."""
    is_valid: bool
    errors: List[ValidationError] = Field(default_factory=list)
    warnings: List[ValidationError] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# API response models
# ---------------------------------------------------------------------------
class InvoiceResponse(BaseModel):
    """
    Response for the upload-invoice endpoint.

    Includes processing status, extracted data, and validation results.
    """
    success: bool
    processing_success: bool = True
    invoice_valid: bool = False
    extracted_data: Optional[InvoiceData] = None
    validation: ValidationResult = Field(
        default_factory=lambda: ValidationResult(is_valid=False)
    )
    processing_notes: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = False
    error_type: str
    message: str
    details: Optional[dict] = None


# ---------------------------------------------------------------------------
# Invoice list models
# ---------------------------------------------------------------------------
class InvoiceListItem(BaseModel):
    """Summary representation of an invoice for list views."""
    id: int
    vendor_name: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    total_amount: Optional[float] = None
    currency: Optional[str] = None
    is_valid: bool
    status: str
    created_at: Optional[str] = None


class InvoiceListResponse(BaseModel):
    """Response for the list-invoices endpoint."""
    count: int
    invoices: List[InvoiceListItem] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Invoice detail model
# ---------------------------------------------------------------------------
class InvoiceDetail(BaseModel):
    """
    Full invoice detail including line items, discount, tax breakdown,
    and validation information.
    """
    id: int
    vendor_name: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None

    # Line items
    line_items: List[LineItem] = Field(default_factory=list)

    # Amounts
    subtotal: Optional[float] = None

    # Discount
    discount_percentage: Optional[float] = None
    discount_amount: Optional[float] = None

    # Tax breakdown
    cgst_rate: Optional[float] = None
    cgst_amount: Optional[float] = None
    sgst_rate: Optional[float] = None
    sgst_amount: Optional[float] = None
    tax: Optional[float] = None

    # Grand total
    total_amount: Optional[float] = None
    currency: Optional[str] = None

    # Status
    is_valid: bool
    status: str
    validation_errors: List[str] = Field(default_factory=list)
    validation_warnings: List[str] = Field(default_factory=list)
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Approval response
# ---------------------------------------------------------------------------
class InvoiceApprovalResponse(BaseModel):
    """
    Response for invoice approval endpoint.

    Phase 2: Simple confirmation of approval action.
    """
    id: int = Field(..., description="Invoice ID")
    status: str = Field(..., description="Updated status (should be APPROVED)")
    message: str = Field(..., description="Confirmation message")
