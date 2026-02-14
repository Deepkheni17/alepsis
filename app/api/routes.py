"""
FastAPI Routes for Invoice Processing

This module defines all API endpoints for the invoice processing backend.
Currently implements: POST /upload-invoice
"""

import logging
import json
from typing import Optional
from fastapi import APIRouter, File, UploadFile, HTTPException, status, Depends, Query, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.models.schemas import (
    InvoiceResponse, 
    ErrorResponse, 
    InvoiceListResponse,
    InvoiceDetail,
    InvoiceApprovalResponse
)
from app.models.orm_models import Invoice
from app.database import get_db
from app.services.ocr import OCRService, OCRNotAvailableError
from app.services.extraction import get_extraction_service
from app.validation.validator import get_validator
from app.services.export import get_export_service

logger = logging.getLogger(__name__)

# Create API router
# Prefix can be added in main.py if needed (e.g., /api/v1)
router = APIRouter()


@router.post(
    "/upload-invoice",
    response_model=InvoiceResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload and process invoice",
    description="""
    Accepts an invoice file (PDF or image), extracts data using AI,
    validates the extracted data, and returns structured JSON.
    
    **Supported formats:** PDF, JPG, JPEG, PNG, TIFF
    
    **Extracted fields:**
    - vendor_name
    - invoice_number
    - invoice_date
    - subtotal
    - tax
    - total_amount
    - currency
    
    **Validation:**
    - Checks if subtotal + tax = total_amount
    - Flags missing required fields
    - Provides warnings for data quality issues
    """,
    responses={
        200: {
            "description": "Invoice processed successfully",
            "model": InvoiceResponse
        },
        400: {
            "description": "Invalid request (unsupported file type, missing file)",
            "model": ErrorResponse
        },
        500: {
            "description": "Internal processing error",
            "model": ErrorResponse
        }
    }
)
async def upload_invoice(
    file: UploadFile = File(..., description="Invoice file (PDF or image)"),
    db: Session = Depends(get_db)
) -> InvoiceResponse:
    """
    Main endpoint for invoice processing.
    
    Process flow:
    1. Validate file type
    2. Extract text via OCR
    3. Extract structured data via AI
    4. Validate extracted data
    5. Return results with validation status
    
    Args:
        file: Uploaded invoice file
        
    Returns:
        InvoiceResponse with extracted data and validation results
        
    Raises:
        HTTPException: If file is invalid or processing fails
    """
    logger.info(f"Received invoice upload: {file.filename}")
    
    try:
        # Step 1: Validate file type
        if not OCRService.validate_file_type(file.filename):
            logger.warning(f"Unsupported file type: {file.filename}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error_type": "INVALID_FILE_TYPE",
                    "message": f"Unsupported file type. Supported: PDF, JPG, PNG, TIFF",
                    "details": {"filename": file.filename}
                }
            )
        
        # Step 2: Read file content
        file_content = await file.read()
        if len(file_content) == 0:
            logger.warning("Empty file uploaded")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error_type": "EMPTY_FILE",
                    "message": "Uploaded file is empty",
                }
            )
        
        # Step 3: Extract text via OCR
        logger.info("Starting OCR extraction")
        try:
            invoice_text = OCRService.extract_text_from_file(file_content, file.filename)
            logger.info("="*70)
            logger.info("OCR EXTRACTION COMPLETE")
            logger.info("="*70)
            logger.info(f"OCR Text Length: {len(invoice_text)} characters")
            logger.info(f"OCR Text Content:\n{invoice_text}")
            logger.info("="*70)
        except OCRNotAvailableError as ocr_error:
            logger.warning(f"OCR not available: {str(ocr_error)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error_type": "OCR_NOT_AVAILABLE",
                    "message": "Cannot process this file: Tesseract-OCR is not installed",
                    "details": {
                        "filename": file.filename,
                        "instructions": str(ocr_error)
                    }
                }
            )
        
        if not invoice_text or len(invoice_text.strip()) < 10:
            logger.warning("OCR returned insufficient text")
            
            # Phase 1: Return with explicit processing status
            empty_validation = get_validator().validate(None, db_session=None)
            return InvoiceResponse(
                success=False,
                processing_success=True,  # Processing ran, but no data extracted
                invoice_valid=False,
                extracted_data=None,
                validation=empty_validation,
                processing_notes="OCR extraction failed or returned no text"
            )
        
        # Step 4: Extract structured data via AI
        logger.info("Starting AI data extraction")
        extraction_service = get_extraction_service()
        extracted_data = extraction_service.extract_invoice_data(invoice_text)
        
        # Step 5: Validate extracted data (Phase 1: with db session for duplicate check)
        logger.info("Starting data validation")
        validator = get_validator()
        validation_result = validator.validate(extracted_data, db_session=db)
        
        # Phase 1: Determine invoice status based on validation
        invoice_status = "PENDING"  # Default
        if len(validation_result.errors) > 0:
            invoice_status = "REVIEW_REQUIRED"  # Has errors, needs review
        # Note: Status remains PENDING even if validation passes
        # APPROVED status will be set manually in future phase
        
        # Step 6: Build response
        success = validation_result.is_valid
        processing_notes = None
        
        if not success:
            processing_notes = f"Found {len(validation_result.errors)} validation errors"
        elif validation_result.warnings:
            processing_notes = f"Extracted successfully with {len(validation_result.warnings)} warnings"
        
        # Step 7: Save to database (Phase 1: Enhanced storage with status)
        try:
            # Phase 1: Store errors and warnings separately but together for safe retrieval
            all_validation_issues = []
            for error in validation_result.errors:
                all_validation_issues.append({
                    "field": error.field,
                    "message": error.message,
                    "severity": error.severity
                })
            for warning in validation_result.warnings:
                all_validation_issues.append({
                    "field": warning.field,
                    "message": warning.message,
                    "severity": warning.severity
                })
            
            # Convert line items to JSON for storage
            line_items_json = None
            if extracted_data and extracted_data.line_items:
                line_items_json = json.dumps([
                    {
                        "product_name": item.product_name,
                        "quantity": item.quantity,
                        "unit_price": item.unit_price,
                        "amount": item.amount
                    }
                    for item in extracted_data.line_items
                ])
            
            invoice_record = Invoice(
                vendor_name=extracted_data.vendor_name if extracted_data else None,
                invoice_number=extracted_data.invoice_number if extracted_data else None,
                invoice_date=extracted_data.invoice_date if extracted_data else None,
                line_items=line_items_json,
                subtotal=extracted_data.subtotal if extracted_data else None,
                discount_percentage=extracted_data.discount_percentage if extracted_data else None,
                discount_amount=extracted_data.discount_amount if extracted_data else None,
                cgst_rate=extracted_data.cgst_rate if extracted_data else None,
                cgst_amount=extracted_data.cgst_amount if extracted_data else None,
                sgst_rate=extracted_data.sgst_rate if extracted_data else None,
                sgst_amount=extracted_data.sgst_amount if extracted_data else None,
                tax=extracted_data.tax if extracted_data else None,
                total_amount=extracted_data.total_amount if extracted_data else None,
                currency=extracted_data.currency if extracted_data else None,
                is_valid=validation_result.is_valid,
                validation_errors=json.dumps(all_validation_issues) if all_validation_issues else None,
                status=invoice_status  # Phase 1: Set status based on validation
            )
            
            db.add(invoice_record)
            db.commit()
            db.refresh(invoice_record)
            logger.info(f"Invoice saved to database with id={invoice_record.id}")
        
        except Exception as db_error:
            logger.error(f"Failed to save invoice to database: {str(db_error)}", exc_info=True)
            db.rollback()
            # Continue execution - don't fail the request if database save fails
        
        logger.info(f"Invoice processing completed: success={success}")
        
        # Phase 1: Return with explicit processing semantics
        return InvoiceResponse(
            success=success,  # Backward compatibility: same as invoice_valid
            processing_success=True,  # Extraction and validation completed
            invoice_valid=validation_result.is_valid,  # Clear validation status
            extracted_data=extracted_data,
            validation=validation_result,
            processing_notes=processing_notes
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        # Log unexpected errors and return 500
        import traceback
        full_traceback = traceback.format_exc()
        logger.error(f"[NEW CODE V2] Unexpected error: {str(e)}")
        logger.error(f"Full traceback:\n{full_traceback}")
        
        # Also write to file for debugging
        try:
            with open("e:/alepsis/error_log.txt", "w") as f:
                f.write(f"Error: {str(e)}\n\n")
                f.write(f"Traceback:\n{full_traceback}\n")
        except:
            pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error_type": "PROCESSING_ERROR",
                "message": "[V2] An unexpected error occurred during invoice processing",
                "details": {"error": str(e), "trace": full_traceback[:200]}
            }
        )


@router.get(
    "/health",
    summary="Health check",
    description="Check if the API is running and healthy",
    status_code=status.HTTP_200_OK
)
async def health_check():
    """
    Simple health check endpoint.
    Useful for monitoring, load balancers, and container orchestration.
    """
    return {
        "status": "healthy",
        "service": "AI Invoice Processing Backend",
        "version": "1.0.0"
    }


# ============================================================================
# READ APIs for Invoice History
# ============================================================================

@router.get(
    "/invoices",
    response_model=InvoiceListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all invoices",
    description="Fetch all processed invoices ordered by creation date (newest first)"
)
async def list_invoices(db: Session = Depends(get_db)) -> InvoiceListResponse:
    """
    Get all invoices from the database.
    
    Returns:
        InvoiceListResponse with count and list of invoices
    """
    try:
        # Fetch all invoices ordered by created_at DESC
        invoices = db.query(Invoice).order_by(Invoice.created_at.desc()).all()
        
        # Convert to response format (Phase 1: includes status)
        invoice_list = [
            {
                "id": inv.id,
                "vendor_name": inv.vendor_name,
                "invoice_number": inv.invoice_number,
                "invoice_date": inv.invoice_date,
                "total_amount": inv.total_amount,
                "currency": inv.currency,
                "is_valid": inv.is_valid,
                "status": inv.status,  # Phase 1: Include status
                "created_at": inv.created_at.isoformat() if inv.created_at else None
            }
            for inv in invoices
        ]
        
        return InvoiceListResponse(
            count=len(invoice_list),
            invoices=invoice_list
        )
    
    except Exception as e:
        logger.error(f"Error fetching invoices: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error_type": "DATABASE_ERROR",
                "message": "Failed to fetch invoices from database"
            }
        )


# ============================================================================
# PHASE 2: EXPORT API - Make Data Usable
# ============================================================================
# CRITICAL: Export route MUST come before /{invoice_id} to avoid path matching issues

@router.get(
    "/invoices/export",
    status_code=status.HTTP_200_OK,
    summary="Export invoices to CSV or Excel",
    description="""
    Export processed invoice data for offline use in accounting software.
    
    **Supported formats:**
    - CSV (default) - Universal compatibility
    - Excel (.xlsx) - For Excel/Google Sheets users
    
    **Optional filtering:**
    - status: Filter by invoice status (PENDING, REVIEW_REQUIRED, APPROVED)
    
    **Examples:**
    - GET /invoices/export → CSV with all invoices
    - GET /invoices/export?format=xlsx → Excel with all invoices
    - GET /invoices/export?format=csv&status=REVIEW_REQUIRED → CSV with only invoices needing review
    
    **Output includes:**
    - All invoice fields
    - Human-readable dates
    - Clean column headers
    - Accountant-friendly formatting
    """,
    responses={
        200: {
            "description": "File download with invoice data",
            "content": {
                "text/csv": {},
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {}
            }
        },
        400: {
            "description": "Invalid parameters",
            "model": ErrorResponse
        },
        500: {
            "description": "Export failed",
            "model": ErrorResponse
        }
    }
)
async def export_invoices(
    format: str = Query(
        default="csv",
        description="Export format: 'csv' or 'xlsx'",
        regex="^(csv|xlsx)$"
    ),
    status: Optional[str] = Query(
        default=None,
        description="Filter by status: PENDING, REVIEW_REQUIRED, or APPROVED"
    ),
    db: Session = Depends(get_db)
) -> Response:
    """
    Phase 2: Export invoices to CSV or Excel format.
    
    Designed for accountants and small businesses to work with invoice data
    in their preferred tools (Excel, Google Sheets, accounting software).
    
    Args:
        format: Export format ('csv' or 'xlsx')
        status: Optional status filter
        db: Database session
        
    Returns:
        File download response with invoice data
        
    Raises:
        HTTPException 400: Invalid parameters
        HTTPException 500: Export generation failed
    """
    logger.info(f"Export request: format={format}, status_filter={status}")
    
    try:
        # Validate status filter if provided
        valid_statuses = ['PENDING', 'REVIEW_REQUIRED', 'APPROVED']
        if status and status.upper() not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error_type": "INVALID_STATUS",
                    "message": f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
                    "details": {"provided_status": status}
                }
            )
        
        # Fetch invoices with optional filtering
        export_service = get_export_service()
        invoices = export_service.fetch_invoices_for_export(
            db=db,
            status_filter=status
        )
        
        # Generate export based on format
        if format == 'xlsx':
            file_content = export_service.export_to_excel(invoices)
        else:  # csv (default)
            file_content = export_service.export_to_csv(invoices)
        
        # Prepare response headers
        filename = export_service.generate_filename(format)
        content_type = export_service.get_content_type(format)
        
        logger.info(f"Export completed: {len(invoices)} invoices exported to {format}")
        
        # Return file download response
        return Response(
            content=file_content,
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Export failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error_type": "EXPORT_ERROR",
                "message": "Failed to generate export file",
                "details": {"error": str(e)}
            }
        )


@router.get(
    "/invoices/{invoice_id}",
    response_model=InvoiceDetail,
    status_code=status.HTTP_200_OK,
    summary="Get invoice by ID",
    description="Fetch detailed information for a specific invoice",
    responses={
        200: {
            "description": "Invoice found",
            "model": InvoiceDetail
        },
        404: {
            "description": "Invoice not found",
            "model": ErrorResponse
        }
    }
)
async def get_invoice(invoice_id: int, db: Session = Depends(get_db)) -> InvoiceDetail:
    """
    Get a single invoice by its ID.
    
    Args:
        invoice_id: Primary key of the invoice
        db: Database session
        
    Returns:
        InvoiceDetail with complete invoice information
        
    Raises:
        HTTPException 404 if invoice not found
    """
    try:
        # Fetch invoice by primary key
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        
        if not invoice:
            logger.warning(f"Invoice not found: id={invoice_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error_type": "NOT_FOUND",
                    "message": f"Invoice with id {invoice_id} not found"
                }
            )
        
        # Parse validation_errors from JSON string (Phase 1: separate errors and warnings)
        validation_errors_list = []
        validation_warnings_list = []
        
        if invoice.validation_errors:
            try:
                all_issues = json.loads(invoice.validation_errors)
                # Phase 1: Separate errors from warnings
                for issue in all_issues:
                    if issue.get("severity") == "error":
                        validation_errors_list.append(f"{issue.get('field', 'unknown')}: {issue.get('message', '')}")
                    elif issue.get("severity") == "warning":
                        validation_warnings_list.append(f"{issue.get('field', 'unknown')}: {issue.get('message', '')}")
            except json.JSONDecodeError:
                logger.warning(f"Could not parse validation_errors for invoice {invoice_id}")
        
        # Parse line items from JSON
        line_items_list = []
        if invoice.line_items:
            try:
                items_data = json.loads(invoice.line_items)
                from app.models.schemas import LineItem
                line_items_list = [LineItem(**item) for item in items_data]
            except json.JSONDecodeError:
                logger.warning(f"Could not parse line_items for invoice {invoice_id}")
        
        return InvoiceDetail(
            id=invoice.id,
            vendor_name=invoice.vendor_name,
            invoice_number=invoice.invoice_number,
            invoice_date=invoice.invoice_date,
            line_items=line_items_list,
            subtotal=invoice.subtotal,
            discount_percentage=invoice.discount_percentage,
            discount_amount=invoice.discount_amount,
            cgst_rate=invoice.cgst_rate,
            cgst_amount=invoice.cgst_amount,
            sgst_rate=invoice.sgst_rate,
            sgst_amount=invoice.sgst_amount,
            tax=invoice.tax,
            total_amount=invoice.total_amount,
            currency=invoice.currency,
            is_valid=invoice.is_valid,
            status=invoice.status,  # Phase 1: Include status
            validation_errors=validation_errors_list,
            validation_warnings=validation_warnings_list,  # Phase 1: Separate warnings
            created_at=invoice.created_at.isoformat() if invoice.created_at else None
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error fetching invoice {invoice_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error_type": "DATABASE_ERROR",
                "message": "Failed to fetch invoice from database"
            }
        )


# ============================================================================
# PHASE 2: APPROVAL WORKFLOW
# ============================================================================

@router.post(
    "/invoices/{invoice_id}/approve",
    response_model=InvoiceApprovalResponse,
    status_code=status.HTTP_200_OK,
    summary="Approve an invoice",
    description="""
    Manually approve an invoice after review.
    
    **Business Rules:**
    - Invoice must exist
    - Cannot approve invoices with status REVIEW_REQUIRED (validation errors present)
    - Changes status from PENDING to APPROVED
    - Already approved invoices can be re-approved (idempotent)
    
    **Use Cases:**
    - Accountant reviews invoice and confirms it's ready for payment
    - Finance manager approves invoices for batch processing
    """,
    responses={
        200: {
            "description": "Invoice approved successfully",
            "model": InvoiceApprovalResponse
        },
        400: {
            "description": "Cannot approve invoice (has validation errors)",
            "model": ErrorResponse
        },
        404: {
            "description": "Invoice not found",
            "model": ErrorResponse
        },
        500: {
            "description": "Approval failed",
            "model": ErrorResponse
        }
    }
)
async def approve_invoice(
    invoice_id: int,
    db: Session = Depends(get_db)
) -> InvoiceApprovalResponse:
    """
    Phase 2: Approve an invoice for payment processing.
    
    Finance-safe workflow: Only invoices without validation errors can be approved.
    
    Args:
        invoice_id: Invoice ID to approve
        db: Database session
        
    Returns:
        InvoiceApprovalResponse with updated status
        
    Raises:
        HTTPException 404: Invoice not found
        HTTPException 400: Invoice has validation errors
        HTTPException 500: Database error
    """
    logger.info(f"Approval request for invoice_id={invoice_id}")
    
    try:
        # Fetch invoice
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        
        if not invoice:
            logger.warning(f"Approval failed: Invoice not found: id={invoice_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error_type": "NOT_FOUND",
                    "message": f"Invoice with id {invoice_id} not found"
                }
            )
        
        # Business rule: Cannot approve invoices with validation errors
        if invoice.status == "REVIEW_REQUIRED":
            logger.warning(f"Approval blocked: Invoice {invoice_id} has validation errors")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error_type": "VALIDATION_ERRORS_PRESENT",
                    "message": "Cannot approve invoice with validation errors. Please review and correct the data first.",
                    "details": {
                        "invoice_id": invoice_id,
                        "current_status": invoice.status,
                        "is_valid": invoice.is_valid
                    }
                }
            )
        
        # Approve invoice (idempotent - can re-approve already approved invoices)
        invoice.status = "APPROVED"
        db.commit()
        db.refresh(invoice)
        
        logger.info(f"Invoice {invoice_id} approved successfully")
        
        return InvoiceApprovalResponse(
            id=invoice.id,
            status=invoice.status,
            message="Invoice approved successfully"
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Approval failed for invoice {invoice_id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error_type": "APPROVAL_ERROR",
                "message": "Failed to approve invoice",
                "details": {"error": str(e)}
            }
        )
