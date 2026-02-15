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
                        # Attempt to repair common JSON issues
                        logger.warning(f"Initial JSON parse failed: {e}. Attempting repair...")
                        repaired_output = self._attempt_json_repair(cleaned_output)
                        
                        try:
                            extracted_json = json.loads(repaired_output)
                            logger.info("Successfully repaired and parsed JSON")
                        except json.JSONDecodeError as e2:
                            error_msg = f"Invalid JSON from LLM: {e2}. Output: {cleaned_output[:500]}"
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
                
                # Parse JSON with error recovery
                try:
                    extracted_json = json.loads(cleaned_output)
                except json.JSONDecodeError as e:
                    # Attempt to repair common JSON issues
                    logger.warning(f"Initial JSON parse failed: {e}. Attempting repair...")
                    repaired_output = self._attempt_json_repair(cleaned_output)
                    
                    try:
                        extracted_json = json.loads(repaired_output)
                        logger.info("Successfully repaired and parsed JSON")
                    except json.JSONDecodeError as e2:
                        error_msg = f"Invalid JSON from LLM: {e2}. Output: {cleaned_output[:500]}"
                        logger.error(error_msg)
                        raise Exception(error_msg)
            else:
                # Unexpected type
                error_msg = f"Unexpected output type from LLM: {type(results.output)}. Value: {results.output}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Validate and convert to InvoiceData
            invoice_data = self._convert_to_invoice_data(extracted_json)
            
            # Apply auto-corrections for obvious math errors
            invoice_data = self._apply_math_corrections(invoice_data)
            
            logger.info(f"Successfully extracted: {invoice_data}")
            return invoice_data
            
        except Exception as e:
            logger.error(f"Extraction failed: {e}", exc_info=True)
            raise
    
    def _build_extraction_prompt(self, invoice_text: str) -> str:
        """Build structured extraction prompt for LLM."""
        return f"""Extract invoice data from the text below and return ONLY valid JSON.

CRITICAL RULES:
1. Return ONLY valid JSON - no explanation, no commentary, no markdown
2. Follow the EXACT schema below - do not add or remove fields
3. Use null for missing values - never guess or leave empty strings
4. Ensure all brackets and braces are properly closed
5. Use double quotes for all strings
6. Numbers must NOT have quotes
7. READ NUMBERS CAREFULLY - extract the EXACT values from the invoice
8. PAY ATTENTION to decimal points and commas in numbers

Required JSON schema (follow EXACTLY):

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

CRITICAL EXTRACTION RULES:
- invoice_date must be YYYY-MM-DD format
- Remove currency symbols from numeric values (₹, $, €, £, etc)
- Numbers must be floats without commas (e.g., "1,234.56" becomes 1234.56)
- Currency must be ISO 3-letter code (USD, EUR, INR, GBP, etc)
- VERIFY that line item amount = quantity × unit_price
- If these don't match, extract the amount shown in the invoice

Line items - EXTRACT CAREFULLY:
- Extract ALL products/services with their EXACT quantity, unit price, and amount
- For each line, look for: product name, quantity (Qty/Nos), rate/price, and total amount
- amount should equal quantity × unit_price - if not, use the amount shown in invoice
- Read numbers from left to right carefully, don't skip digits

Subtotal:
- This is the sum of all line item amounts BEFORE discount and tax
- Look for "Subtotal", "Sub Total", "Amount Before Tax"
- If not explicitly mentioned, sum all line item amounts

Discount:
- Extract both percentage (% rate) and amount (₹ value) if available
- Look for "Discount", "Less Discount", "Reduction"
- If only percentage given, calculate: discount_amount = subtotal × (percentage/100)

Tax breakdown - READ CAREFULLY:
- cgst_rate and cgst_amount: Central GST rate (%) and amount (₹)
- sgst_rate and sgst_amount: State GST rate (%) and amount (₹)
- tax: TOTAL of all taxes (sum of CGST + SGST + IGST + any other tax amounts)
- Look for "CGST", "Central Tax", "SGST", "State Tax", "UTGST", "IGST"

Grand Total:
- total_amount: Final payable amount (after discount and tax)
- Formula: subtotal - discount_amount + tax = total_amount
- Look for "Grand Total", "Total Amount", "Net Payable", "Amount Due", "Total"

COMMON MISTAKES TO AVOID:
- Don't confuse quantity with unit price
- Don't confuse subtotal with total_amount
- Don't mix up CGST and SGST amounts
- Don't skip decimal points
- Don't reverse digits when reading numbers

Invoice text:
{invoice_text}"""
    
    def _clean_json_output(self, output: str) -> str:
        """
        Clean and repair JSON output from LLM.
        Handles markdown, common formatting issues, and attempts repair.
        """
        output = output.strip()
        
        # Remove markdown json blocks
        if output.startswith("```json"):
            output = output[7:]
        elif output.startswith("```"):
            output = output[3:]
        
        if output.endswith("```"):
            output = output[:-3]
        
        output = output.strip()
        
        # Try to find JSON object boundaries if output contains extra text
        if output and not output.startswith('{'):
            # Look for first opening brace
            start_idx = output.find('{')
            if start_idx != -1:
                output = output[start_idx:]
        
        if output and not output.endswith('}'):
            # Look for last closing brace
            end_idx = output.rfind('}')
            if end_idx != -1:
                output = output[:end_idx + 1]
        
        return output
    
    def _attempt_json_repair(self, json_str: str) -> str:
        """
        Attempt to repair common JSON formatting issues.
        This is a best-effort approach for malformed LLM output.
        """
        import re
        
        # Remove any non-printable characters
        json_str = ''.join(char for char in json_str if char.isprintable() or char in '\n\r\t')
        
        # Fix common issues with corrupted field names like {"n  "field": ...
        # This happens when LLM output gets corrupted
        json_str = re.sub(r'\{\s*"n\s+"', '{"', json_str)
        
        # Fix missing commas between objects in arrays
        json_str = re.sub(r'\}\s*\{', '},{', json_str)
        
        # Fix missing commas between fields
        json_str = re.sub(r'"\s*\n\s*"', '",\n"', json_str)
        
        # Remove trailing commas before closing braces/brackets
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        return json_str
    
    def _apply_math_corrections(self, invoice_data: InvoiceData) -> InvoiceData:
        """
        Apply automatic corrections for obvious mathematical errors in extracted data.
        This helps compensate for LLM extraction mistakes.
        """
        logger.info("Applying math corrections to extracted invoice data...")
        
        # Fix line item amounts if qty × price doesn't match
        for i, item in enumerate(invoice_data.line_items):
            if item.quantity is not None and item.unit_price is not None:
                calculated_amount = round(item.quantity * item.unit_price, 2)
                if item.amount is not None:
                    # Check if the amount is significantly different
                    diff = abs(calculated_amount - item.amount)
                    if diff > 0.01:  # More than 1 cent difference
                        logger.warning(f"Line item {i}: Correcting amount from {item.amount} to {calculated_amount} (Qty {item.quantity} × Price {item.unit_price})")
                        item.amount = calculated_amount
                else:
                    logger.info(f"Line item {i}: Calculating amount as {calculated_amount}")
                    item.amount = calculated_amount
        
        # Recalculate subtotal from line items if there's a mismatch
        if invoice_data.line_items:
            calculated_subtotal = sum(
                item.amount for item in invoice_data.line_items 
                if item.amount is not None
            )
            calculated_subtotal = round(calculated_subtotal, 2)
            
            if invoice_data.subtotal is not None:
                diff = abs(calculated_subtotal - invoice_data.subtotal)
                if diff > 0.5:  # Significant difference
                    logger.warning(f"Subtotal mismatch: Extracted={invoice_data.subtotal}, Calculated={calculated_subtotal}. Using calculated value.")
                    invoice_data.subtotal = calculated_subtotal
            else:
                logger.info(f"Setting subtotal to calculated value: {calculated_subtotal}")
                invoice_data.subtotal = calculated_subtotal
        
        # Fix discount_amount if percentage is given but amount is wrong
        if invoice_data.discount_percentage is not None and invoice_data.subtotal is not None:
            calculated_discount = round((invoice_data.subtotal * invoice_data.discount_percentage) / 100, 2)
            if invoice_data.discount_amount is not None:
                diff = abs(calculated_discount - invoice_data.discount_amount)
                if diff > 0.5:
                    logger.warning(f"Discount amount mismatch: Extracted={invoice_data.discount_amount}, Calculated={calculated_discount}. Using calculated value.")
                    invoice_data.discount_amount = calculated_discount
            else:
                logger.info(f"Calculating discount amount: {calculated_discount}")
                invoice_data.discount_amount = calculated_discount
        
        # Sum up total tax from components if available
        if invoice_data.cgst_amount is not None or invoice_data.sgst_amount is not None:
            calculated_tax = 0.0
            if invoice_data.cgst_amount is not None:
                calculated_tax += invoice_data.cgst_amount
            if invoice_data.sgst_amount is not None:
                calculated_tax += invoice_data.sgst_amount
            
            calculated_tax = round(calculated_tax, 2)
            
            if invoice_data.tax is not None:
                diff = abs(calculated_tax - invoice_data.tax)
                if diff > 0.5 and calculated_tax > 0:
                    logger.warning(f"Tax mismatch: Extracted={invoice_data.tax}, Calculated={calculated_tax}. Using calculated value.")
                    invoice_data.tax = calculated_tax
            elif calculated_tax > 0:
                logger.info(f"Setting tax to calculated value: {calculated_tax}")
                invoice_data.tax = calculated_tax
        
        # Verify and fix total_amount using formula: subtotal - discount + tax
        if invoice_data.subtotal is not None:
            calculated_total = invoice_data.subtotal
            
            if invoice_data.discount_amount is not None:
                calculated_total -= invoice_data.discount_amount
            
            if invoice_data.tax is not None:
                calculated_total += invoice_data.tax
            
            calculated_total = round(calculated_total, 2)
            
            if invoice_data.total_amount is not None:
                diff = abs(calculated_total - invoice_data.total_amount)
                if diff > 0.5:
                    logger.warning(f"Total amount mismatch: Extracted={invoice_data.total_amount}, Calculated={calculated_total}. Using calculated value.")
                    invoice_data.total_amount = calculated_total
            else:
                logger.info(f"Setting total amount to calculated value: {calculated_total}")
                invoice_data.total_amount = calculated_total
        
        logger.info("Math corrections completed")
        return invoice_data
    
    def _convert_to_invoice_data(self, data: Dict[str, Any]) -> InvoiceData:
        """Convert and validate extracted JSON to InvoiceData model."""
        from app.models.schemas import LineItem
        
        # Helper function to safely extract numeric value
        def safe_float(value):
            if value is None:
                return None
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                # Remove currency symbols and commas
                value = value.replace(',', '').replace('₹', '').replace('$', '').replace('€', '').replace('£', '').strip()
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return None
            if isinstance(value, dict):
                # Handle cases where LLM returns object instead of number
                # Try to extract 'amount' field if present
                if 'amount' in value:
                    return safe_float(value['amount'])
                return None
            return None
        
        # Convert line items
        line_items = []
        if data.get("line_items"):
            for item in data["line_items"]:
                line_items.append(LineItem(
                    product_name=item.get("product_name"),
                    quantity=safe_float(item.get("quantity")),
                    unit_price=safe_float(item.get("unit_price")),
                    amount=safe_float(item.get("amount"))
                ))
        
        return InvoiceData(
            vendor_name=data.get("vendor_name"),
            invoice_number=str(data.get("invoice_number")) if data.get("invoice_number") is not None else None,
            invoice_date=data.get("invoice_date"),
            line_items=line_items,
            subtotal=safe_float(data.get("subtotal")),
            discount_percentage=safe_float(data.get("discount_percentage")),
            discount_amount=safe_float(data.get("discount_amount")),
            cgst_rate=safe_float(data.get("cgst_rate")),
            cgst_amount=safe_float(data.get("cgst_amount")),
            sgst_rate=safe_float(data.get("sgst_rate")),
            sgst_amount=safe_float(data.get("sgst_amount")),
            tax=safe_float(data.get("tax")),
            total_amount=safe_float(data.get("total_amount")),
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
