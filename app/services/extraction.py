"""
Invoice Data Extraction Service

Extracts structured data from invoice text using Bytez SDK with Google Gemma.
Production-safe with comprehensive error handling and logging.
"""

import json
import logging
import os
from typing import Optional, Dict, Any
from app.models.schemas import InvoiceData

logger = logging.getLogger(__name__)

try:
    from bytez import Bytez
    BYTEZ_AVAILABLE = True
except ImportError:
    BYTEZ_AVAILABLE = False
    logger.error("Bytez library not installed. Run: pip install bytez")


class LLMExtractionService:
    """
    Production-ready LLM-based invoice extraction service using Bytez SDK.
    """
    
    def __init__(self):
        """Initialize the Bytez LLM extraction service."""
        if not BYTEZ_AVAILABLE:
            raise RuntimeError("Bytez library not available. Install with: pip install bytez")
        
        api_key = "0fc77d4f062bcae74f6807f37ba1da07"
        
        try:
            self.sdk = Bytez(api_key)
            self.model = self.sdk.model("meta-llama/Llama-3.2-3B-Instruct")
            logger.info("LLM extraction service initialized with meta-llama/Llama-3.2-3B-Instruct")
        except Exception as e:
            logger.error(f"Failed to initialize Bytez SDK: {e}")
            raise RuntimeError(f"Bytez SDK initialization failed: {e}")
    
    def extract_invoice_data(self, invoice_text: str) -> InvoiceData:
        """
        Extract structured invoice data from raw text using LLM.
        
        Args:
            invoice_text: Raw OCR-extracted invoice text
            
        Returns:
            InvoiceData: Pydantic model with extracted fields
            
        Raises:
            Exception: If LLM returns invalid JSON or encounters errors
        """
        logger.info("Starting LLM-based invoice extraction")
        logger.info(f"Input text length: {len(invoice_text)} characters")
        
        prompt = self._build_extraction_prompt(invoice_text)
        
        try:
            logger.info("Calling LLM model...")
            results = self.model.run([
                {
                    "role": "user",
                    "content": prompt
                }
            ])
            logger.info("LLM model call completed")
            
            if results.error:
                error_msg = f"LLM API error: {results.error}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Log the type and value of output for debugging
            logger.info(f"results.output type: {type(results.output)}")
            logger.info(f"results.output value: {str(results.output)[:300]}...")
            
            # Handle the response format from Bytez
            # The output is typically a dict like: {'role': 'assistant', 'content': '...', 'tool_calls': []}
            if isinstance(results.output, dict) and 'content' in results.output:
                # Extract the content field
                raw_output = results.output['content']
                logger.info(f"LLM returned dict with content field")
                
                # The content should be a string containing JSON
                if isinstance(raw_output, str):
                    raw_output = raw_output.strip()
                    cleaned_output = self._clean_json_output(raw_output)
                    
                    try:
                        extracted_json = json.loads(cleaned_output)
                    except json.JSONDecodeError as e:
                        error_msg = f"Invalid JSON from LLM: {e}. Output: {cleaned_output[:500]}"
                        logger.error(error_msg)
                        raise Exception(error_msg)
                else:
                    # Content is already parsed
                    logger.info(f"Content field is not string, type: {type(raw_output)}")
                    extracted_json = raw_output
                    
            elif isinstance(results.output, dict):
                # LLM returned a dict directly (without content field) - use it as is
                logger.info(f"LLM returned dict without content field")
                extracted_json = results.output
            elif isinstance(results.output, str):
                # LLM returned a string - parse it
                raw_output = results.output.strip() if results.output else ""
                logger.info(f"LLM raw string output: {raw_output[:200]}...")
                
                # Clean potential markdown wrapping
                cleaned_output = self._clean_json_output(raw_output)
                
                # Parse JSON
                try:
                    extracted_json = json.loads(cleaned_output)
                except json.JSONDecodeError as e:
                    error_msg = f"Invalid JSON from LLM: {e}. Output: {cleaned_output[:500]}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
            else:
                # Unexpected type
                error_msg = f"Unexpected output type from LLM: {type(results.output)}. Value: {results.output}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Validate and convert to InvoiceData
            invoice_data = self._convert_to_invoice_data(extracted_json)
            
            logger.info(f"Successfully extracted: {invoice_data}")
            return invoice_data
            
        except Exception as e:
            logger.error(f"Extraction failed: {e}", exc_info=True)
            raise
    
    def _build_extraction_prompt(self, invoice_text: str) -> str:
        """Build structured extraction prompt for LLM."""
        return f"""Extract complete invoice data from the text below.

Return ONLY valid JSON.
Do NOT explain.
Do NOT add commentary.
Do NOT wrap in markdown.
Do NOT guess missing values.
If a field cannot be found, return null.

Required JSON schema:

{{
  "vendor_name": string | null,
  "invoice_number": string | null,
  "invoice_date": string | null,
  "line_items": [
    {{
      "product_name": string | null,
      "quantity": number | null,
      "unit_price": number | null,
      "amount": number | null
    }}
  ],
  "subtotal": number | null,
  "discount_percentage": number | null,
  "discount_amount": number | null,
  "cgst_rate": number | null,
  "cgst_amount": number | null,
  "sgst_rate": number | null,
  "sgst_amount": number | null,
  "tax": number | null,
  "total_amount": number | null,
  "currency": string | null
}}

Extraction rules:
- invoice_date must be YYYY-MM-DD format
- Remove currency symbols from numeric values (₹, $, €, £, etc)
- Numbers must be floats without commas
- Currency must be ISO 3-letter code (USD, EUR, INR, GBP, etc)

Line items:
- Extract ALL products/services with their quantity, unit price, and amount
- amount should equal quantity × unit_price
- If only total amount is shown for an item, extract that as amount

Subtotal:
- Sum of all line item amounts BEFORE discount and tax
- If not explicitly mentioned, calculate from line items

Discount:
- Extract both percentage and amount if available
- Look for terms like "Discount", "Less", "Reduction"

Tax breakdown:
- cgst_rate and cgst_amount: Central GST (percentage and amount)
- sgst_rate and sgst_amount: State/UT GST (percentage and amount)
- tax: Total of all taxes (CGST + SGST + IGST + any other tax)
- Look for terms like "CGST", "Central Tax", "SGST", "State Tax", "UTGST"

Grand Total:
- total_amount: Final payable amount (after discount and tax)
- Look for "Grand Total", "Total Amount", "Net Payable", "Amount Due"

Do NOT confuse subtotal with total.
If uncertain about any field, return null.

Invoice text:
{invoice_text}"""
    
    def _clean_json_output(self, output: str) -> str:
        """Remove markdown code blocks if present."""
        output = output.strip()
        
        # Remove markdown json blocks
        if output.startswith("```json"):
            output = output[7:]
        elif output.startswith("```"):
            output = output[3:]
        
        if output.endswith("```"):
            output = output[:-3]
        
        return output.strip()
    
    def _convert_to_invoice_data(self, data: Dict[str, Any]) -> InvoiceData:
        """Convert and validate extracted JSON to InvoiceData model."""
        from app.models.schemas import LineItem
        
        # Convert line items
        line_items = []
        if data.get("line_items"):
            for item in data["line_items"]:
                line_items.append(LineItem(
                    product_name=item.get("product_name"),
                    quantity=float(item["quantity"]) if item.get("quantity") is not None else None,
                    unit_price=float(item["unit_price"]) if item.get("unit_price") is not None else None,
                    amount=float(item["amount"]) if item.get("amount") is not None else None
                ))
        
        return InvoiceData(
            vendor_name=data.get("vendor_name"),
            invoice_number=str(data.get("invoice_number")) if data.get("invoice_number") is not None else None,
            invoice_date=data.get("invoice_date"),
            line_items=line_items,
            subtotal=float(data["subtotal"]) if data.get("subtotal") is not None else None,
            discount_percentage=float(data["discount_percentage"]) if data.get("discount_percentage") is not None else None,
            discount_amount=float(data["discount_amount"]) if data.get("discount_amount") is not None else None,
            cgst_rate=float(data["cgst_rate"]) if data.get("cgst_rate") is not None else None,
            cgst_amount=float(data["cgst_amount"]) if data.get("cgst_amount") is not None else None,
            sgst_rate=float(data["sgst_rate"]) if data.get("sgst_rate") is not None else None,
            sgst_amount=float(data["sgst_amount"]) if data.get("sgst_amount") is not None else None,
            tax=float(data["tax"]) if data.get("tax") is not None else None,
            total_amount=float(data["total_amount"]) if data.get("total_amount") is not None else None,
            currency=data.get("currency")
        )


# Legacy alias for backward compatibility
class ExtractionService(LLMExtractionService):
    """Alias for backward compatibility."""
    pass


# Singleton instance
_extraction_service = None


def get_extraction_service() -> LLMExtractionService:
    """Get or create singleton LLM extraction service instance."""
    global _extraction_service
    if _extraction_service is None:
        _extraction_service = LLMExtractionService()
    return _extraction_service
