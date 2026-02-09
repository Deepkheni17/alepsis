"""
FastAPI Routes for Invoice Processing

This module defines all API endpoints for the invoice processing backend.
Currently implements: POST /upload-invoice
"""

import logging
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse

from app.models.schemas import InvoiceResponse, ErrorResponse
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
    file: UploadFile = File(..., description="Invoice file (PDF or image)")
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
