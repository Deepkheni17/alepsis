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
    5. Data Integrity: Check for duplicates and consistency
    6. Line Items: Validate individual product line math
    """

    # Tolerance for floating-point comparison (0.01 = 1 cent)
    AMOUNT_TOLERANCE = 0.01
    # Allow slightly more tolerance for subtotal aggregation (rounding across items)
    SUBTOTAL_TOLERANCE = 1.0

    def validate(self, invoice_data: InvoiceData, db_session=None) -> ValidationResult:
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
        errors.extend(self._check_amount_integrity(invoice_data))
        errors.extend(self._check_mathematical_consistency(invoice_data))

        # Line item validations
        errors.extend(self._check_line_item_math(invoice_data))
        warnings.extend(self._check_subtotal_consistency(invoice_data))
        warnings.extend(self._check_discount_consistency(invoice_data))

        # Check for duplicates if database session provided
        if db_session:
            errors.extend(self._check_duplicate_invoice(invoice_data, db_session))

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

        # Critical fields that must be present (errors if missing)
        critical_fields = {
            'vendor_name': 'Vendor name',
            'invoice_number': 'Invoice number',
        }

        for field, display_name in critical_fields.items():
            value = getattr(data, field, None)
            if value is None or (isinstance(value, str) and not value.strip()):
                errors.append(ValidationError(
                    field=field,
                    message=f"{display_name} is missing but required for processing",
                    severity="error"
                ))

        return errors

    def _check_amount_integrity(self, data: InvoiceData) -> List[ValidationError]:
        """
        Validate amount fields for critical issues.

        Errors:
        - Missing subtotal or total_amount (critical for accounting)
        - Negative amounts (likely data errors, not credit notes)
        """
        errors = []

        # Subtotal and total_amount are critical for financial processing
        if data.subtotal is None:
            errors.append(ValidationError(
                field="subtotal",
                message="Subtotal is missing - required for accounting verification",
                severity="error"
            ))

        if data.total_amount is None:
            errors.append(ValidationError(
                field="total_amount",
                message="Total amount is missing - required for payment processing",
                severity="error"
            ))

        # Check for negative amounts (likely extraction errors)
        if data.subtotal is not None and data.subtotal < 0:
            errors.append(ValidationError(
                field="subtotal",
                message=f"Subtotal is negative ({data.subtotal:.2f}) - likely extraction error",
                severity="error"
            ))

        if data.total_amount is not None and data.total_amount < 0:
            errors.append(ValidationError(
                field="total_amount",
                message=f"Total amount is negative ({data.total_amount:.2f}) - likely extraction error",
                severity="error"
            ))

        if data.tax is not None and data.tax < 0:
            errors.append(ValidationError(
                field="tax",
                message=f"Tax is negative ({data.tax:.2f}) - likely extraction error",
                severity="error"
            ))

        return errors

    def _check_duplicate_invoice(self, data: InvoiceData, db_session) -> List[ValidationError]:
        """
        Check for duplicate invoice numbers in database.
        """
        errors = []

        # Only check if invoice_number is present
        if not data.invoice_number:
            return errors

        try:
            from app.models.orm_models import Invoice

            # Check if invoice_number already exists
            existing = db_session.query(Invoice).filter(
                Invoice.invoice_number == data.invoice_number
            ).first()

            if existing:
                errors.append(ValidationError(
                    field="invoice_number",
                    message=f"Invoice number '{data.invoice_number}' already exists (ID: {existing.id})",
                    severity="error"
                ))
                logger.warning(f"Duplicate invoice number detected: {data.invoice_number}")

        except Exception as e:
            # Never crash validation due to DB errors
            logger.error(f"Error checking for duplicate invoice: {str(e)}", exc_info=True)

        return errors

    def _check_mathematical_consistency(self, data: InvoiceData) -> List[ValidationError]:
        """
        Validate that subtotal - discount + tax = total_amount.
        This is the core business validation.
        """
        errors = []

        # Only validate if subtotal and total are present
        if data.subtotal is None or data.total_amount is None:
            return errors

        # Calculate expected total: subtotal - discount + tax
        discount = data.discount_amount or 0.0
        tax = data.tax or 0.0
        calculated_total = data.subtotal - discount + tax
        difference = abs(calculated_total - data.total_amount)

        if difference > self.AMOUNT_TOLERANCE:
            errors.append(ValidationError(
                field="total_amount",
                message=(
                    f"Math error: Subtotal ({data.subtotal:.2f}) - "
                    f"Discount ({discount:.2f}) + "
                    f"Tax ({tax:.2f}) = {calculated_total:.2f}, "
                    f"but Grand Total is {data.total_amount:.2f}. "
                    f"Difference: {difference:.2f}"
                ),
                severity="error"
            ))
            logger.warning(f"Mathematical inconsistency detected: {difference:.2f} difference")

        return errors

    def _check_line_item_math(self, data: InvoiceData) -> List[ValidationError]:
        """
        Validate that quantity × unit_price = amount for each line item.
        """
        errors = []

        for idx, item in enumerate(data.line_items):
            if item.quantity is not None and item.unit_price is not None and item.amount is not None:
                expected = item.quantity * item.unit_price
                difference = abs(expected - item.amount)

                if difference > self.AMOUNT_TOLERANCE:
                    name = item.product_name or f"Item #{idx + 1}"
                    errors.append(ValidationError(
                        field=f"line_items[{idx}]",
                        message=(
                            f"{name}: Qty ({item.quantity}) × Price ({item.unit_price:.2f}) "
                            f"= {expected:.2f}, but Amount is {item.amount:.2f}"
                        ),
                        severity="error"
                    ))

        return errors

    def _check_subtotal_consistency(self, data: InvoiceData) -> List[ValidationError]:
        """
        Warn if sum of line item amounts doesn't match subtotal.
        This is a warning (not error) because rounding differences are common.
        """
        warnings = []

        if not data.line_items or data.subtotal is None:
            return warnings

        # Only check if we have items with amounts
        items_with_amounts = [i for i in data.line_items if i.amount is not None]
        if not items_with_amounts:
            return warnings

        items_sum = sum(i.amount for i in items_with_amounts)
        difference = abs(items_sum - data.subtotal)

        if difference > self.SUBTOTAL_TOLERANCE:
            warnings.append(ValidationError(
                field="subtotal",
                message=(
                    f"Sum of line items ({items_sum:.2f}) doesn't match "
                    f"subtotal ({data.subtotal:.2f}). Difference: {difference:.2f}"
                ),
                severity="warning"
            ))

        return warnings

    def _check_discount_consistency(self, data: InvoiceData) -> List[ValidationError]:
        """
        Warn if discount_percentage and discount_amount don't align with subtotal.
        """
        warnings = []

        if (data.discount_percentage is not None
                and data.discount_amount is not None
                and data.subtotal is not None):
            expected_discount = data.subtotal * data.discount_percentage / 100.0
            difference = abs(expected_discount - data.discount_amount)

            if difference > self.AMOUNT_TOLERANCE:
                warnings.append(ValidationError(
                    field="discount_amount",
                    message=(
                        f"Discount {data.discount_percentage}% of {data.subtotal:.2f} "
                        f"= {expected_discount:.2f}, but discount amount is {data.discount_amount:.2f}"
                    ),
                    severity="warning"
                ))

        return warnings

    def _check_data_quality(self, data: InvoiceData) -> List[ValidationError]:
        """
        Check for data quality issues that don't prevent processing
        but should be flagged to users.
        """
        warnings = []

        # Warn if tax is missing
        if data.tax is None:
            warnings.append(ValidationError(
                field="tax",
                message="Tax amount is missing - may affect tax reporting and reconciliation",
                severity="warning"
            ))

        # Warn if invoice date is missing
        if data.invoice_date is None or (isinstance(data.invoice_date, str) and not data.invoice_date.strip()):
            warnings.append(ValidationError(
                field="invoice_date",
                message="Invoice date is missing - may affect accounting period assignment",
                severity="warning"
            ))

        # Warn if currency is not specified
        if data.currency is None or (isinstance(data.currency, str) and not data.currency.strip()):
            warnings.append(ValidationError(
                field="currency",
                message="Currency not detected - assuming default currency (may cause issues in multi-currency accounting)",
                severity="warning"
            ))

        # Warn if amounts are unusually large (potential OCR error)
        if data.total_amount is not None and data.total_amount > 1_000_000:
            warnings.append(ValidationError(
                field="total_amount",
                message=f"Unusually large amount ({data.total_amount:.2f}) - verify accuracy",
                severity="warning"
            ))

        # Warn if no line items found
        if not data.line_items:
            warnings.append(ValidationError(
                field="line_items",
                message="No line items extracted - product details may be missing from the invoice",
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

    """
    Validates extracted invoice data against business rules.
    
    Validation Categories:
    1. Completeness: Are required fields present?
    2. Format: Are values in correct format?
    3. Mathematical: Do amounts add up correctly?
    4. Business Logic: Do values make business sense?
    5. Data Integrity: Check for duplicates and consistency
    
    Phase 1 Enhancement: Added trust & safety validations
    """
    
    # Tolerance for floating-point comparison (0.01 = 1 cent)
    AMOUNT_TOLERANCE = 0.01
    
    def validate(self, invoice_data: InvoiceData, db_session=None) -> ValidationResult:
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
        errors.extend(self._check_amount_integrity(invoice_data))
        errors.extend(self._check_mathematical_consistency(invoice_data))
        
        # Check for duplicates if database session provided
        if db_session:
            errors.extend(self._check_duplicate_invoice(invoice_data, db_session))
        
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
        
        Phase 1: Enhanced to check subtotal and total_amount as critical
        """
        errors = []
        
        # Critical fields that must be present (errors if missing)
        critical_fields = {
            'vendor_name': 'Vendor name',
            'invoice_number': 'Invoice number',
        }
        
        for field, display_name in critical_fields.items():
            value = getattr(data, field, None)
            if value is None or (isinstance(value, str) and not value.strip()):
                errors.append(ValidationError(
                    field=field,
                    message=f"{display_name} is missing but required for processing",
                    severity="error"
                ))
        
        return errors
    
    def _check_amount_integrity(self, data: InvoiceData) -> List[ValidationError]:
        """
        Phase 1: Validate amount fields for critical issues.
        
        Errors:
        - Missing subtotal or total_amount (critical for accounting)
        - Negative amounts (likely data errors, not credit notes)
        """
        errors = []
        
        # Subtotal and total_amount are critical for financial processing
        if data.subtotal is None:
            errors.append(ValidationError(
                field="subtotal",
                message="Subtotal is missing - required for accounting verification",
                severity="error"
            ))
        
        if data.total_amount is None:
            errors.append(ValidationError(
                field="total_amount",
                message="Total amount is missing - required for payment processing",
                severity="error"
            ))
        
        # Check for negative amounts (likely extraction errors)
        if data.subtotal is not None and data.subtotal < 0:
            errors.append(ValidationError(
                field="subtotal",
                message=f"Subtotal is negative ({data.subtotal:.2f}) - likely extraction error",
                severity="error"
            ))
        
        if data.total_amount is not None and data.total_amount < 0:
            errors.append(ValidationError(
                field="total_amount",
                message=f"Total amount is negative ({data.total_amount:.2f}) - likely extraction error",
                severity="error"
            ))
        
        if data.tax is not None and data.tax < 0:
            errors.append(ValidationError(
                field="tax",
                message=f"Tax is negative ({data.tax:.2f}) - likely extraction error",
                severity="error"
            ))
        
        return errors
    
    def _check_duplicate_invoice(self, data: InvoiceData, db_session) -> List[ValidationError]:
        """
        Phase 1: Check for duplicate invoice numbers in database.
        
        Note: Basic check only. Does not prevent race conditions.
        For production, add unique constraint + proper error handling.
        """
        errors = []
        
        # Only check if invoice_number is present
        if not data.invoice_number:
            return errors
        
        try:
            from app.models.orm_models import Invoice
            
            # Check if invoice_number already exists
            existing = db_session.query(Invoice).filter(
                Invoice.invoice_number == data.invoice_number
            ).first()
            
            if existing:
                errors.append(ValidationError(
                    field="invoice_number",
                    message=f"Invoice number '{data.invoice_number}' already exists (ID: {existing.id})",
                    severity="error"
                ))
                logger.warning(f"Duplicate invoice number detected: {data.invoice_number}")
        
        except Exception as e:
            # Never crash validation due to DB errors
            logger.error(f"Error checking for duplicate invoice: {str(e)}", exc_info=True)
        
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
        Phase 1 Enhanced: Check for data quality issues that don't prevent processing
        but should be flagged to users.
        
        Added warnings:
        - Missing tax (important for reconciliation)
        - Missing invoice_date (affects accounting periods)
        - Missing currency (affects multi-currency handling)
        """
        warnings = []
        
        # Phase 1: Warn if tax is missing
        if data.tax is None:
            warnings.append(ValidationError(
                field="tax",
                message="Tax amount is missing - may affect tax reporting and reconciliation",
                severity="warning"
            ))
        
        # Phase 1: Warn if invoice date is missing
        if data.invoice_date is None or (isinstance(data.invoice_date, str) and not data.invoice_date.strip()):
            warnings.append(ValidationError(
                field="invoice_date",
                message="Invoice date is missing - may affect accounting period assignment",
                severity="warning"
            ))
        
        # Phase 1: Warn if currency is not specified
        if data.currency is None or (isinstance(data.currency, str) and not data.currency.strip()):
            warnings.append(ValidationError(
                field="currency",
                message="Currency not detected - assuming default currency (may cause issues in multi-currency accounting)",
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
