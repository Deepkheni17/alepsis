"""
FastAPI Routes for Invoice Processing

This module defines all API endpoints for the invoice processing backend.
Currently implements: POST /upload-invoice
"""

import logging
import json
from fastapi import APIRouter, File, UploadFile, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.models.schemas import (
    InvoiceResponse, 
    ErrorResponse, 
    InvoiceListResponse,
    InvoiceDetail
)
from app.models.orm_models import Invoice
from app.database import get_db
from app.services.ocr import OCRService
from app.services.extraction import get_extraction_service
from app.validation.validator import get_validator

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
        invoice_text = OCRService.extract_text_from_file(file_content, file.filename)
        
        if not invoice_text or len(invoice_text.strip()) < 10:
            logger.warning("OCR returned insufficient text")
            return InvoiceResponse(
                success=False,
                extracted_data=None,
                validation=get_validator().validate(None),
                processing_notes="OCR extraction failed or returned no text"
            )
        
        # Step 4: Extract structured data via AI
        logger.info("Starting AI data extraction")
        extraction_service = get_extraction_service()
        extracted_data = extraction_service.extract_invoice_data(invoice_text)
        
        # Step 5: Validate extracted data
        logger.info("Starting data validation")
        validator = get_validator()
        validation_result = validator.validate(extracted_data)
        
        # Step 6: Build response
        success = validation_result.is_valid
        processing_notes = None
        
        if not success:
            processing_notes = f"Found {len(validation_result.errors)} validation errors"
        elif validation_result.warnings:
            processing_notes = f"Extracted successfully with {len(validation_result.warnings)} warnings"
        
        # Step 7: Save to database
        try:
            # Combine errors and warnings into JSON string
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
            
            invoice_record = Invoice(
                vendor_name=extracted_data.vendor_name if extracted_data else None,
                invoice_number=extracted_data.invoice_number if extracted_data else None,
                invoice_date=extracted_data.invoice_date if extracted_data else None,
                subtotal=extracted_data.subtotal if extracted_data else None,
                tax=extracted_data.tax if extracted_data else None,
                total_amount=extracted_data.total_amount if extracted_data else None,
                currency=extracted_data.currency if extracted_data else None,
                is_valid=validation_result.is_valid,
                validation_errors=json.dumps(all_validation_issues) if all_validation_issues else None
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
        
        return InvoiceResponse(
            success=success,
            extracted_data=extracted_data,
            validation=validation_result,
            processing_notes=processing_notes
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        # Log unexpected errors and return 500
        logger.error(f"Unexpected error processing invoice: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error_type": "PROCESSING_ERROR",
                "message": "An unexpected error occurred during invoice processing",
                "details": {"error": str(e)}
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
        
        # Convert to response format
        invoice_list = [
            {
                "id": inv.id,
                "vendor_name": inv.vendor_name,
                "invoice_number": inv.invoice_number,
                "invoice_date": inv.invoice_date,
                "total_amount": inv.total_amount,
                "currency": inv.currency,
                "is_valid": inv.is_valid,
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
        
        # Parse validation_errors from JSON string
        validation_errors_list = []
        if invoice.validation_errors:
            try:
                validation_errors_list = json.loads(invoice.validation_errors)
            except json.JSONDecodeError:
                logger.warning(f"Could not parse validation_errors for invoice {invoice_id}")
        
        return InvoiceDetail(
            id=invoice.id,
            vendor_name=invoice.vendor_name,
            invoice_number=invoice.invoice_number,
            invoice_date=invoice.invoice_date,
            subtotal=invoice.subtotal,
            tax=invoice.tax,
            total_amount=invoice.total_amount,
            currency=invoice.currency,
            is_valid=invoice.is_valid,
            validation_errors=validation_errors_list,
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
