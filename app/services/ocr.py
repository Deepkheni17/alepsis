"""
Mock OCR Service
In production, this would integrate with:
- Azure Computer Vision
- AWS Textract
- Google Cloud Vision
- Tesseract OCR
- PyPDF2 for text extraction from PDFs

For MVP purposes, we simulate OCR output with realistic invoice text.
"""

from typing import BinaryIO
import logging

logger = logging.getLogger(__name__)


class OCRService:
    """
    Mock OCR service that simulates text extraction from invoice documents.
    In production, replace this with actual OCR integration.
    """
    
    @staticmethod
    def extract_text_from_file(file_content: bytes, filename: str) -> str:
        """
        Simulates OCR text extraction from invoice file.
        
        Args:
            file_content: Raw bytes of the uploaded file
            filename: Original filename (used to determine file type)
            
        Returns:
            Extracted text from the document
            
        Note:
            In production, this would:
            1. Detect file type (PDF, JPG, PNG, etc.)
            2. Call appropriate OCR engine
            3. Handle multi-page documents
            4. Return cleaned, structured text
        """
        logger.info(f"Processing file: {filename} ({len(file_content)} bytes)")
        
        # Mock response - simulates realistic invoice text
        # In production, this would be the actual OCR output
        mock_invoice_text = """
        INVOICE
        
        ABC Corporation
        123 Business Street
        New York, NY 10001
        
        Invoice Number: INV-2024-001234
        Date: 2024-01-15
        
        Bill To:
        Client Company Inc.
        456 Customer Ave
        Los Angeles, CA 90001
        
        Description                    Quantity    Price       Amount
        ----------------------------------------------------------------
        Professional Services          10 hrs      $150.00     $1,500.00
        Consulting Fee                 5 hrs       $200.00     $1,000.00
        Software License               1           $500.00     $500.00
        
        Subtotal:                                              $3,000.00
        Tax (8.5%):                                            $255.00
        ----------------------------------------------------------------
        TOTAL DUE:                                             $3,255.00
        
        Currency: USD
        Payment Terms: Net 30
        """
        
        logger.info("OCR extraction completed successfully")
        return mock_invoice_text.strip()
    
    @staticmethod
    def validate_file_type(filename: str) -> bool:
        """
        Validates that the uploaded file is a supported format.
        
        Args:
            filename: Name of the uploaded file
            
        Returns:
            True if file type is supported, False otherwise
        """
        supported_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.tif'}
        file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
        return f'.{file_ext}' in supported_extensions
