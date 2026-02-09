"""
AI-Powered Invoice Data Extraction Service

This service extracts structured data from invoice text using LLM-based parsing.
In production, integrate with:
- OpenAI GPT-4
- Azure OpenAI
- Anthropic Claude
- Google Gemini
- Open-source models (LLaMA, Mistral, etc.)

For MVP, we use rule-based extraction with patterns that simulate AI extraction.
"""

import re
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.schemas import InvoiceData

logger = logging.getLogger(__name__)


class ExtractionService:
    """
    Extracts structured invoice data from raw text.
    
    In production, this would:
    1. Call LLM API with structured prompt
    2. Use JSON mode or function calling
    3. Implement retry logic and error handling
    4. Cache results for cost optimization
    """
    
    def __init__(self):
        """Initialize the extraction service."""
        self.patterns = self._build_extraction_patterns()
    
    def _build_extraction_patterns(self) -> Dict[str, re.Pattern]:
        """
        Build regex patterns for data extraction.
        In production, LLM would handle this more intelligently.
        """
        return {
            'invoice_number': re.compile(r'Invoice\s+(?:Number|#|No\.?)[\s:]*([A-Z0-9-]+)', re.IGNORECASE),
            'vendor_name': re.compile(r'([A-Z][A-Za-z\s&,\.]+(?:Corporation|Corp|Inc|LLC|Ltd|Company))', re.IGNORECASE),
            'invoice_date': re.compile(r'(?:Date|Invoice Date)[\s:]*(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})', re.IGNORECASE),
            'subtotal': re.compile(r'Subtotal[\s:]+\$?([\d,]+\.\d{2})', re.IGNORECASE),
            'tax': re.compile(r'Tax[^:]*[\s:]+\$?([\d,]+\.\d{2})', re.IGNORECASE),
            'total': re.compile(r'TOTAL\s+DUE[\s:]+\$?([\d,]+\.\d{2})', re.IGNORECASE),
            'currency': re.compile(r'Currency[\s:]*([A-Z]{3})', re.IGNORECASE),
        }
    
    def extract_invoice_data(self, invoice_text: str) -> InvoiceData:
        """
        Extract structured invoice data from raw text.
        
        Args:
            invoice_text: Raw text extracted via OCR
            
        Returns:
            InvoiceData object with extracted fields
            
        Note:
            In production, this would be an LLM API call like:
            ```python
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Extract invoice data as JSON..."},
                    {"role": "user", "content": invoice_text}
                ],
                response_format={"type": "json_object"}
            )
            ```
        """
        logger.info("Starting invoice data extraction")
        
        # Extract each field using pattern matching
        # In production, LLM would handle this with better context understanding
        extracted_data = {
            'vendor_name': self._extract_vendor_name(invoice_text),
            'invoice_number': self._extract_field(invoice_text, 'invoice_number'),
            'invoice_date': self._extract_and_normalize_date(invoice_text),
            'subtotal': self._extract_amount(invoice_text, 'subtotal'),
            'tax': self._extract_amount(invoice_text, 'tax'),
            'total_amount': self._extract_amount(invoice_text, 'total'),
            'currency': self._extract_currency(invoice_text),
        }
        
        logger.info(f"Extraction completed. Found {sum(1 for v in extracted_data.values() if v is not None)} fields")
        return InvoiceData(**extracted_data)
    
    def _extract_field(self, text: str, field_name: str) -> Optional[str]:
        """Extract a single field using regex pattern."""
        pattern = self.patterns.get(field_name)
        if not pattern:
            return None
        
        match = pattern.search(text)
        return match.group(1).strip() if match else None
    
    def _extract_vendor_name(self, text: str) -> Optional[str]:
        """
        Extract vendor name (first company name found after INVOICE header).
        LLM would be smarter about distinguishing vendor from customer.
        """
        # Find all matches
        matches = self.patterns['vendor_name'].findall(text)
        if matches:
            # Filter out header-only words and get first valid company name
            for vendor in matches:
                vendor_clean = vendor.strip()
                # Skip if it's just a header word like "INVOICE" alone
                if vendor_clean.upper() not in ['INVOICE', 'BILL', 'RECEIPT', 'STATEMENT']:
                    # Clean up whitespace
                    vendor_clean = re.sub(r'\s+', ' ', vendor_clean)
                    return vendor_clean
        return None
    
    def _extract_amount(self, text: str, field_name: str) -> Optional[float]:
        """Extract and parse monetary amount."""
        value = self._extract_field(text, field_name)
        if value:
            try:
                # Remove commas and convert to float
                cleaned = value.replace(',', '')
                return float(cleaned)
            except (ValueError, AttributeError):
                logger.warning(f"Failed to parse {field_name}: {value}")
                return None
        return None
    
    def _extract_and_normalize_date(self, text: str) -> Optional[str]:
        """
        Extract and normalize date to YYYY-MM-DD format.
        LLM would handle various date formats more robustly.
        """
        date_str = self._extract_field(text, 'invoice_date')
        if not date_str:
            return None
        
        try:
            # Try parsing common date formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    return parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            logger.warning(f"Could not parse date: {date_str}")
            return date_str  # Return as-is if parsing fails
        except Exception as e:
            logger.error(f"Date extraction error: {e}")
            return None
    
    def _extract_currency(self, text: str) -> Optional[str]:
        """
        Extract currency code.
        Defaults to USD if $ symbol found but no explicit currency.
        """
        currency = self._extract_field(text, 'currency')
        if currency:
            return currency.upper()
        
        # Check for dollar sign as fallback
        if '$' in text:
            return 'USD'
        
        return None


# Singleton instance
_extraction_service = None


def get_extraction_service() -> ExtractionService:
    """
    Get or create singleton extraction service instance.
    This pattern facilitates dependency injection and testing.
    """
    global _extraction_service
    if _extraction_service is None:
        _extraction_service = ExtractionService()
    return _extraction_service
