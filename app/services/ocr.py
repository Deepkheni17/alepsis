"""
OCR Service for Invoice Processing
Extracts text from PDF and image files using:
- PyPDF2 for text extraction from PDFs
- pytesseract for OCR on images
- pdf2image to convert PDFs to images when needed
"""

import io
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class OCRNotAvailableError(Exception):
    """Raised when OCR is needed but Tesseract is not installed."""
    pass


# Module-level initialization
try:
    import pytesseract
    from PIL import Image, ImageEnhance
    from pdf2image import convert_from_bytes
    import PyPDF2
    
    OCR_LIBRARIES_AVAILABLE = True
    TESSERACT_AVAILABLE = False
    
    # Check for Tesseract availability
    tesseract_cmd = os.getenv('TESSERACT_CMD')
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        logger.info(f"Using Tesseract from TESSERACT_CMD: {tesseract_cmd}")
    
    try:
        pytesseract.get_tesseract_version()
        TESSERACT_AVAILABLE = True
        logger.info("Tesseract-OCR is available and ready")
    except Exception as e:
        logger.warning(f"Tesseract-OCR not found: {e}")
        logger.warning("Image and scanned PDF processing will not be available")
        logger.warning("To enable: Install Tesseract and add to PATH, or set TESSERACT_CMD environment variable")
        
except ImportError as e:
    logger.error(f"OCR libraries not installed: {e}")
    OCR_LIBRARIES_AVAILABLE = False
    TESSERACT_AVAILABLE = False


class OCRService:
    """
    Production-safe OCR service for invoice documents.
    Supports digital PDFs, scanned PDFs, and images.
    """
    
    @staticmethod
    def extract_text_from_file(file_content: bytes, filename: str) -> str:
        """
        Extract text from invoice file using appropriate method.
        
        Args:
            file_content: Raw bytes of the uploaded file
            filename: Original filename for type detection
            
        Returns:
            Extracted text from the document
            
        Raises:
            OCRNotAvailableError: When OCR is needed but Tesseract unavailable
            ValueError: For unsupported file types
            Exception: For other processing errors
        """
        if not OCR_LIBRARIES_AVAILABLE:
            raise Exception("OCR libraries not installed. Install pytesseract, Pillow, pdf2image, and PyPDF2")
        
        logger.info(f"Processing: {filename} ({len(file_content)} bytes)")
        
        file_ext = Path(filename).suffix.lower()
        
        try:
            if file_ext == '.pdf':
                return OCRService._handle_pdf(file_content, filename)
            elif file_ext in {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp'}:
                return OCRService._handle_image(file_content, filename)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
                
        except OCRNotAvailableError:
            raise
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"OCR processing failed for {filename}: {e}", exc_info=True)
            raise Exception(f"Failed to extract text: {str(e)}")
    
    @staticmethod
    def _handle_pdf(file_content: bytes, filename: str) -> str:
        """Handle PDF file: try text extraction first, then OCR if needed."""
        # Attempt direct text extraction
        text = OCRService._extract_text_from_pdf(file_content)
        
        if text and len(text.strip()) > 50:
            logger.info(f"Extracted {len(text)} chars from digital PDF")
            return text.strip()
        
        # PDF is scanned or has no text - needs OCR
        logger.info("PDF appears scanned, attempting OCR")
        
        if not TESSERACT_AVAILABLE:
            raise OCRNotAvailableError(
                "This PDF contains no extractable text (scanned image). "
                "Tesseract-OCR is required.\n\n"
                "Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki\n"
                "Then restart the backend or set TESSERACT_CMD environment variable."
            )
        
        return OCRService._ocr_pdf(file_content)
    
    @staticmethod
    def _handle_image(file_content: bytes, filename: str) -> str:
        """Handle image file: perform OCR."""
        if not TESSERACT_AVAILABLE:
            raise OCRNotAvailableError(
                "Tesseract-OCR is required to process image files.\n\n"
                "Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki\n"
                "Then restart the backend or set TESSERACT_CMD environment variable."
            )
        
        text = OCRService._ocr_image(file_content)
        logger.info(f"Extracted {len(text)} chars from image via OCR")
        return text.strip()
    
    @staticmethod
    def _extract_text_from_pdf(file_content: bytes) -> str:
        """Extract text directly from PDF using PyPDF2."""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_parts = []
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            
            return "\n".join(text_parts)
            
        except Exception as e:
            logger.warning(f"PDF text extraction failed: {e}")
            return ""
    
    @staticmethod
    def _ocr_pdf(file_content: bytes) -> str:
        """Convert PDF pages to images and perform OCR."""
        try:
            images = convert_from_bytes(file_content)
            
            text_parts = []
            for i, image in enumerate(images, start=1):
                logger.info(f"OCR processing page {i}/{len(images)}")
                preprocessed = OCRService._preprocess_image(image)
                page_text = pytesseract.image_to_string(preprocessed)
                if page_text.strip():
                    text_parts.append(page_text)
            
            return "\n".join(text_parts)
            
        except Exception as e:
            logger.error(f"PDF OCR failed: {e}")
            raise Exception(f"Failed to OCR PDF: {str(e)}")
    
    @staticmethod
    def _ocr_image(file_content: bytes) -> str:
        """Perform OCR on image file with preprocessing."""
        try:
            image = Image.open(io.BytesIO(file_content))
            preprocessed = OCRService._preprocess_image(image)
            text = pytesseract.image_to_string(preprocessed)
            return text
            
        except Exception as e:
            logger.error(f"Image OCR failed: {e}")
            raise Exception(f"Failed to OCR image: {str(e)}")
    
    @staticmethod
    def _preprocess_image(image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR accuracy."""
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Optional: Convert to grayscale for better OCR on some documents
        # Uncomment if needed:
        # image = image.convert('L')
        
        return image
    
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
