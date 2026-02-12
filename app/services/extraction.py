"""
Invoice Data Extraction Service

Extracts structured data from invoice text using rule-based patterns.
Production-safe with comprehensive error handling and logging.
"""

import re
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.schemas import InvoiceData

logger = logging.getLogger(__name__)


class ExtractionService:
    """
    Production-safe invoice data extraction service.
    Uses regex patterns to extract structured data from raw invoice text.
    """
    
    def __init__(self):
        """Initialize the extraction service."""
        self.patterns = self._build_extraction_patterns()
    
    def _build_extraction_patterns(self) -> Dict[str, re.Pattern]:
        """Build regex patterns for extracting invoice fields."""
        return {
            'invoice_number': re.compile(
                r'(?:Invoice|INV|Invoice\s+No|Invoice\s+Number|#)[\s:.#-]*([A-Z0-9-]+)',
                re.IGNORECASE
            ),
            'vendor_name': re.compile(
                r'(?:From|Vendor|Bill\s+From|Billed\s+By)?[\s:]*'
                r'([A-Z][A-Za-z\s&,\.]+(?:Corporation|Corp|Inc|LLC|Ltd|Company|Co\.|Pvt|Limited))',
                re.IGNORECASE
            ),
            'invoice_date': re.compile(
                r'(?:Date|Invoice\s+Date|Dated|Issue\s+Date)[\s:]*'
                r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|'
                r'\d{4}[-/]\d{1,2}[-/]\d{1,2}|'
                r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})',
                re.IGNORECASE
            ),
            'subtotal': re.compile(
                r'(?:Sub[\s-]?total|Amount)[\s:$]*\$?\s*([\d,]+\.?\d{0,2})',
                re.IGNORECASE
            ),
            'tax': re.compile(
                r'(?:Tax|VAT|GST|Sales\s+Tax)(?:\s+\([^)]+\))?[\s:$]*\$?\s*([\d,]+\.?\d{0,2})',
                re.IGNORECASE
            ),
            'total': re.compile(
                r'(?:Total|Grand\s+Total|Amount\s+Due|Total\s+Due|Balance\s+Due)[\s:$]*\$?\s*([\d,]+\.?\d{0,2})',
                re.IGNORECASE
            ),
            'currency': re.compile(r'(?:Currency|Curr)[\s:]*([A-Z]{3})', re.IGNORECASE),
        }
    
    def extract_invoice_data(self, invoice_text: str) -> InvoiceData:
        """
        Extract structured invoice data from raw text.
        Never crashes - returns InvoiceData with available fields.
        
        Args:
            invoice_text: Raw text extracted via OCR
            
        Returns:
            InvoiceData object with extracted fields (nulls where not found)
        """
        logger.info("Starting invoice data extraction")
        
        try:
            extracted_data = {
                'vendor_name': self._extract_vendor_name(invoice_text),
                'invoice_number': self._extract_field(invoice_text, 'invoice_number'),
                'invoice_date': self._extract_and_normalize_date(invoice_text),
                'subtotal': self._extract_amount(invoice_text, 'subtotal'),
                'tax': self._extract_amount(invoice_text, 'tax'),
                'total_amount': self._extract_amount(invoice_text, 'total'),
                'currency': self._extract_currency(invoice_text),
            }
            
            # Log extraction results
            found_count = sum(1 for v in extracted_data.values() if v is not None)
            logger.info(f"Extraction completed. Found {found_count}/7 fields")
            
            # Log missing fields for debugging
            missing = [k for k, v in extracted_data.items() if v is None]
            if missing:
                logger.warning(f"Missing fields: {', '.join(missing)}")
            
            return InvoiceData(**extracted_data)
            
        except Exception as e:
            logger.error(f"Extraction failed: {e}", exc_info=True)
            # Return empty invoice data rather than crashing
            return InvoiceData()
    
    def _extract_field(self, text: str, field_name: str) -> Optional[str]:
        """Extract a single field using regex pattern. Never crashes."""
        try:
            pattern = self.patterns.get(field_name)
            if not pattern:
                return None
            
            match = pattern.search(text)
            return match.group(1).strip() if match else None
        except Exception as e:
            logger.warning(f"Failed to extract {field_name}: {e}")
            return None
    
    def _extract_vendor_name(self, text: str) -> Optional[str]:
        """Extract vendor name with fallback logic. Never crashes."""
        try:
            # First try pattern match for company names
            matches = self.patterns['vendor_name'].findall(text)
            if matches:
                for vendor in matches:
                    vendor_clean = re.sub(r'\s+', ' ', vendor.strip())
                    # Filter out header-only words
                    if vendor_clean.upper() not in {'INVOICE', 'BILL', 'RECEIPT', 'STATEMENT'}:
                        return vendor_clean
            
            # Fallback: Look for capitalized names in first 500 chars
            first_part = text[:500]
            name_pattern = re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b')
            names = name_pattern.findall(first_part)
            
            excluded = {'INVOICE', 'BILL', 'TO', 'FROM', 'DATE', 'NUMBER', 'AMOUNT', 'TOTAL'}
            for name in names:
                if name.upper() not in excluded:
                    return name
            
            return None
        except Exception as e:
            logger.warning(f"Vendor name extraction failed: {e}")
            return None
    
    def _extract_amount(self, text: str, field_name: str) -> Optional[float]:
        """
        Extract and parse monetary amount with safe conversion.
        Handles currency symbols, commas, and malformed input.
        """
        try:
            value = self._extract_field(text, field_name)
            if value:
                # Remove currency symbols and commas
                cleaned = re.sub(r'[$€£¥,]', '', value).strip()
                try:
                    return float(cleaned)
                except (ValueError, TypeError):
                    logger.warning(f"Cannot parse amount for {field_name}: '{value}'")
            
            # Fallback for 'total': find largest amount
            if field_name == 'total':
                amounts = re.findall(r'[\d,]+\.?\d{0,2}', text)
                if amounts:
                    float_amounts = []
                    for amt in amounts:
                        try:
                            float_amounts.append(float(amt.replace(',', '')))
                        except ValueError:
                            continue
                    if float_amounts:
                        return max(float_amounts)
            
            return None
        except Exception as e:
            logger.warning(f"Amount extraction failed for {field_name}: {e}")
            return None
    
    def _extract_and_normalize_date(self, text: str) -> Optional[str]:
        """
        Extract and normalize date to YYYY-MM-DD format.
        Tries multiple date formats. Never crashes.
        """
        try:
            date_str = self._extract_field(text, 'invoice_date')
            if not date_str:
                return None
            
            # Try parsing various formats
            date_formats = [
                '%Y-%m-%d',      # 2024-01-15
                '%m/%d/%Y',      # 01/15/2024
                '%d/%m/%Y',      # 15/01/2024
                '%m-%d-%Y',      # 01-15-2024
                '%d-%m-%Y',      # 15-01-2024
                '%Y/%m/%d',      # 2024/01/15
                '%B %d, %Y',     # January 15, 2024
                '%b %d, %Y',     # Jan 15, 2024
                '%d %B %Y',      # 15 January 2024
                '%d %b %Y',      # 15 Jan 2024
            ]
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    return parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            # If no format matches, return as-is
            logger.warning(f"Could not parse date '{date_str}' - returning raw value")
            return date_str
            
        except Exception as e:
            logger.warning(f"Date extraction failed: {e}")
            return None
    
    def _extract_currency(self, text: str) -> Optional[str]:
        """Extract currency code with fallback to USD for $. Never crashes."""
        try:
            currency = self._extract_field(text, 'currency')
            if currency:
                return currency.upper()
            
            # Fallback: Check for dollar sign
            if '$' in text:
                return 'USD'
            
            return None
        except Exception as e:
            logger.warning(f"Currency extraction failed: {e}")
            return None


# Singleton instance
_extraction_service = None


def get_extraction_service() -> ExtractionService:
    """Get or create singleton extraction service instance."""
    global _extraction_service
    if _extraction_service is None:
        _extraction_service = ExtractionService()
    return _extraction_service
