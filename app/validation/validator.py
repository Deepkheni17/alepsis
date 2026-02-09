"""
Invoice Data Validation Service

Implements business logic validation for extracted invoice data.
Ensures data integrity and flags potential errors without failing the request.

Key Principle: Fail safely, never silently.
- We flag errors clearly
- We provide actionable error messages
- We don't reject requests; we inform users of issues
"""

import logging
from typing import List
from app.models.schemas import InvoiceData, ValidationResult, ValidationError

logger = logging.getLogger(__name__)


class InvoiceValidator:
    """
    Validates extracted invoice data against business rules.
    
    Validation Categories:
    1. Completeness: Are required fields present?
    2. Format: Are values in correct format?
    3. Mathematical: Do amounts add up correctly?
    4. Business Logic: Do values make business sense?
    """
    
    # Tolerance for floating-point comparison (0.01 = 1 cent)
    AMOUNT_TOLERANCE = 0.01
    
    def validate(self, invoice_data: InvoiceData) -> ValidationResult:
        """
        Validate invoice data and return structured validation results.
        
        Args:
            invoice_data: Extracted invoice data to validate
            
        Returns:
            ValidationResult with all errors and warnings
        """
        logger.info("Starting invoice data validation")
        
        errors: List[ValidationError] = []
        warnings: List[ValidationError] = []
        
        # Run all validation checks
        errors.extend(self._check_required_fields(invoice_data))
        errors.extend(self._check_mathematical_consistency(invoice_data))
        warnings.extend(self._check_data_quality(invoice_data))
        
        is_valid = len(errors) == 0
        
        logger.info(f"Validation complete: {len(errors)} errors, {len(warnings)} warnings")
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings
        )
    
    def _check_required_fields(self, data: InvoiceData) -> List[ValidationError]:
        """
        Check that critical fields are present.
        These are fields typically required for accounting systems.
        """
        errors = []
        required_fields = {
            'vendor_name': 'Vendor name',
            'invoice_number': 'Invoice number',
            'total_amount': 'Total amount',
        }
        
        for field, display_name in required_fields.items():
            value = getattr(data, field, None)
            if value is None:
                errors.append(ValidationError(
                    field=field,
                    message=f"{display_name} is missing but required for processing",
                    severity="error"
                ))
        
        return errors
    
    def _check_mathematical_consistency(self, data: InvoiceData) -> List[ValidationError]:
        """
        Validate that subtotal + tax = total_amount.
        This is the core business validation requested.
        """
        errors = []
        
        # Only validate if all three amounts are present
        if data.subtotal is None or data.tax is None or data.total_amount is None:
            # Don't error on missing data - that's handled by required fields check
            return errors
        
        # Calculate expected total
        calculated_total = data.subtotal + data.tax
        difference = abs(calculated_total - data.total_amount)
        
        if difference > self.AMOUNT_TOLERANCE:
            errors.append(ValidationError(
                field="total_amount",
                message=(
                    f"Math error: Subtotal ({data.subtotal:.2f}) + "
                    f"Tax ({data.tax:.2f}) = {calculated_total:.2f}, "
                    f"but Total is {data.total_amount:.2f}. "
                    f"Difference: {difference:.2f}"
                ),
                severity="error"
            ))
            logger.warning(f"Mathematical inconsistency detected: {difference:.2f} difference")
        
        return errors
    
    def _check_data_quality(self, data: InvoiceData) -> List[ValidationError]:
        """
        Check for data quality issues that don't prevent processing
        but should be flagged to users.
        """
        warnings = []
        
        # Warn if invoice date is missing
        if data.invoice_date is None:
            warnings.append(ValidationError(
                field="invoice_date",
                message="Invoice date is missing - may affect accounting period assignment",
                severity="warning"
            ))
        
        # Warn if currency is not specified
        if data.currency is None:
            warnings.append(ValidationError(
                field="currency",
                message="Currency not detected - assuming default currency",
                severity="warning"
            ))
        
        # Warn if amounts are negative
        if data.total_amount is not None and data.total_amount < 0:
            warnings.append(ValidationError(
                field="total_amount",
                message="Total amount is negative - verify this is a credit note",
                severity="warning"
            ))
        
        # Warn if amounts are unusually large (potential OCR error)
        if data.total_amount is not None and data.total_amount > 1_000_000:
            warnings.append(ValidationError(
                field="total_amount",
                message=f"Unusually large amount ({data.total_amount:.2f}) - verify accuracy",
                severity="warning"
            ))
        
        return warnings


# Singleton instance
_validator = None


def get_validator() -> InvoiceValidator:
    """
    Get or create singleton validator instance.
    This pattern facilitates dependency injection and testing.
    """
    global _validator
    if _validator is None:
        _validator = InvoiceValidator()
    return _validator
