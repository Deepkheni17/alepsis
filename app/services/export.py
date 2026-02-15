"""
Invoice Export Service

Phase 2: Export processed invoices to CSV and Excel formats.
Accountant-friendly output with clean, readable data.
"""

import io
import logging
from datetime import datetime
from typing import List, Optional
import pandas as pd
from sqlalchemy.orm import Session

from app.models.orm_models import Invoice

logger = logging.getLogger(__name__)


class InvoiceExportService:
    """
    Service for exporting invoice data to various formats.
    
    Phase 2: Focuses on CSV and Excel export for accountant workflows.
    Keeps data clean, readable, and compatible with standard tools.
    """
    
    @staticmethod
    def export_to_csv(invoices: List[Invoice]) -> bytes:
        """
        Export invoices to CSV format.
        
        Args:
            invoices: List of Invoice ORM objects
            
        Returns:
            CSV file content as bytes
        """
        logger.info(f"Exporting {len(invoices)} invoices to CSV")
        
        # Convert to DataFrame for clean CSV generation
        df = InvoiceExportService._prepare_dataframe(invoices)
        
        # Generate CSV in memory
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8')
        csv_content = output.getvalue().encode('utf-8')
        
        return csv_content
    
    @staticmethod
    def export_to_excel(invoices: List[Invoice]) -> bytes:
        """
        Export invoices to Excel format (.xlsx).
        
        Args:
            invoices: List of Invoice ORM objects
            
        Returns:
            Excel file content as bytes
        """
        logger.info(f"Exporting {len(invoices)} invoices to Excel")
        
        # Convert to DataFrame
        df = InvoiceExportService._prepare_dataframe(invoices)
        
        # Generate Excel in memory
        output = io.BytesIO()
        
        # Use openpyxl engine for .xlsx format
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Invoices', index=False)
        
        excel_content = output.getvalue()
        
        return excel_content
    
    @staticmethod
    def _prepare_dataframe(invoices: List[Invoice]) -> pd.DataFrame:
        """
        Convert invoice ORM objects to clean pandas DataFrame.
        
        Phase 2: Focus on accountant-friendly data:
        - Clean column names
        - Readable dates
        - Numeric types preserved
        - Missing values handled gracefully
        
        Args:
            invoices: List of Invoice ORM objects
            
        Returns:
            DataFrame with clean, export-ready data
        """
        # Extract data from ORM objects
        data = []
        for inv in invoices:
            data.append({
                'ID': inv.id,
                'Vendor Name': inv.vendor_name if inv.vendor_name else '',
                'Invoice Number': inv.invoice_number if inv.invoice_number else '',
                'Invoice Date': inv.invoice_date if inv.invoice_date else '',
                'Subtotal': inv.subtotal if inv.subtotal is not None else '',
                'Discount %': inv.discount_percentage if inv.discount_percentage is not None else '',
                'Discount Amount': inv.discount_amount if inv.discount_amount is not None else '',
                'CGST Rate %': inv.cgst_rate if inv.cgst_rate is not None else '',
                'CGST Amount': inv.cgst_amount if inv.cgst_amount is not None else '',
                'SGST Rate %': inv.sgst_rate if inv.sgst_rate is not None else '',
                'SGST Amount': inv.sgst_amount if inv.sgst_amount is not None else '',
                'Total Tax': inv.tax if inv.tax is not None else '',
                'Grand Total': inv.total_amount if inv.total_amount is not None else '',
                'Currency': inv.currency if inv.currency else '',
                'Valid': 'Yes' if inv.is_valid else 'No',
                'Status': inv.status,
                'Created At': inv.created_at.strftime('%Y-%m-%d %H:%M:%S') if inv.created_at else ''
            })
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # If no data, return empty DataFrame with headers
        if df.empty:
            df = pd.DataFrame(columns=[
                'ID', 'Vendor Name', 'Invoice Number', 'Invoice Date',
                'Subtotal', 'Discount %', 'Discount Amount',
                'CGST Rate %', 'CGST Amount', 'SGST Rate %', 'SGST Amount',
                'Total Tax', 'Grand Total', 'Currency',
                'Valid', 'Status', 'Created At'
            ])
        
        return df
    
    @staticmethod
    def generate_filename(format: str) -> str:
        """
        Generate a meaningful export filename with timestamp.
        
        Args:
            format: File format ('csv' or 'xlsx')
            
        Returns:
            Filename string (e.g., 'invoices_export_2024-01-15.csv')
        """
        today = datetime.now().strftime('%Y-%m-%d')
        return f"invoices_export_{today}.{format}"
    
    @staticmethod
    def get_content_type(format: str) -> str:
        """
        Get appropriate Content-Type header for format.
        
        Args:
            format: File format ('csv' or 'xlsx')
            
        Returns:
            MIME type string
        """
        if format == 'xlsx':
            return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        else:  # csv
            return 'text/csv'
    
    @staticmethod
    def fetch_invoices_for_export(
        db: Session, 
        status_filter: Optional[str] = None,
        user_id: Optional[object] = None
    ) -> List[Invoice]:
        """
        Fetch invoices from database with optional filtering.
        
        Phase 2: Minimal, safe filtering by status and user.
        
        Args:
            db: Database session
            status_filter: Optional status to filter by (PENDING, REVIEW_REQUIRED, APPROVED)
            user_id: Optional user UUID to filter by (for multi-user support)
            
        Returns:
            List of Invoice objects ordered by creation date (newest first)
        """
        query = db.query(Invoice).order_by(Invoice.created_at.desc())
        
        # Apply user filter if provided (multi-user support)
        if user_id:
            query = query.filter(Invoice.user_id == user_id)
            logger.info(f"Filtering export by user_id: {user_id}")
        
        # Apply status filter if provided
        if status_filter:
            query = query.filter(Invoice.status == status_filter.upper())
            logger.info(f"Filtering export by status: {status_filter}")
        
        invoices = query.all()
        logger.info(f"Fetched {len(invoices)} invoices for export")
        
        return invoices


# Singleton instance
_export_service = None


def get_export_service() -> InvoiceExportService:
    """
    Get or create singleton export service instance.
    Facilitates dependency injection and testing.
    """
    global _export_service
    if _export_service is None:
        _export_service = InvoiceExportService()
    return _export_service
