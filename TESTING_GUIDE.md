# Invoice Processing System - Testing Guide

## System Overview

Complete invoice processing system with:
- **Backend**: FastAPI on `http://127.0.0.1:8000`
- **Frontend**: Next.js on `http://localhost:3000`
- **Database**: SQLite (`invoices.db`)

## Quick Start

### 1. Start Backend (Terminal 1)
```powershell
cd e:\alepsis
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. Start Frontend (Terminal 2)
```powershell
cd e:\alepsis\frontend
npm run dev
```

### 3. Access Applications
- **Frontend UI**: http://localhost:3000
- **Backend API Docs**: http://127.0.0.1:8000/docs

## Testing Workflow

### Test 1: Upload Invoice
1. Open http://localhost:3000/upload
2. Click "Choose File" and select an invoice image
3. Click "Upload"
4. Verify extracted data is displayed
5. Check validation errors/warnings
6. Note the invoice status (PENDING, REVIEW_REQUIRED, or APPROVED)

### Test 2: View Invoice List
1. Navigate to http://localhost:3000/invoices
2. Verify table shows all invoices with:
   - ID, Vendor, Invoice #, Date, Total, Status
   - View and Approve buttons (where applicable)
3. Test status badges (color-coded)

### Test 3: View Invoice Details
1. Click "View" on any invoice from the list
2. Verify detailed view shows:
   - All extracted fields
   - Validation errors (red) and warnings (orange)
   - Current status
   - Approve button (if status is PENDING)

### Test 4: Approve Invoice
1. Find a PENDING invoice
2. Click "Approve Invoice" button
3. Confirm the approval dialog
4. Verify:
   - Success message appears
   - Status updates to APPROVED
   - Approve button disappears

**Note**: Invoices with status REVIEW_REQUIRED cannot be approved (backend validation)

### Test 5: Export Data
1. From dashboard (http://localhost:3000), click:
   - "Export All as CSV"
   - "Export All as Excel"
2. Verify files download correctly
3. Open files to verify data formatting

### Test 6: Dashboard Summary
1. Go to http://localhost:3000
2. Verify summary cards show correct counts:
   - Total invoices
   - Pending count
   - Review Required count
   - Approved count
3. Test quick action buttons

## API Endpoints (Direct Testing)

### Backend API Documentation
Access interactive API docs at http://127.0.0.1:8000/docs

### Key Endpoints
- `POST /upload-invoice` - Upload invoice image
- `GET /invoices` - List all invoices
- `GET /invoices/{id}` - Get invoice details
- `POST /invoices/{id}/approve` - Approve invoice
- `GET /invoices/export?format=csv|xlsx&status=PENDING|REVIEW_REQUIRED|APPROVED` - Export data

## Validation Rules

### Critical Errors (REVIEW_REQUIRED status)
- Missing vendor name
- Missing invoice number
- Missing or negative total amount
- Duplicate invoice (same vendor + invoice number)

### Warnings (PENDING status)
- Missing tax information
- Missing invoice date
- Missing currency

## Expected Behavior

### Status Workflow
1. **PENDING**: Invoice passes validation with no critical errors
   - Can be approved via frontend or API
   
2. **REVIEW_REQUIRED**: Invoice has critical validation errors
   - Cannot be approved (backend rejects)
   - Must be manually reviewed and corrected
   
3. **APPROVED**: Invoice has been explicitly approved
   - Cannot be re-approved
   - Final state

### Frontend Features
- ✅ Responsive design with Tailwind CSS
- ✅ Client-side state management for dynamic updates
- ✅ Loading states during API calls
- ✅ Error handling with user-friendly messages
- ✅ Color-coded status badges
- ✅ Conditional UI (approve button visibility)

## Troubleshooting

### Frontend can't reach backend
- Verify backend is running on port 8000
- Check Next.js proxy config in `next.config.js`
- Look for CORS errors in browser console

### "Cannot approve invoice" error
- Check invoice status - REVIEW_REQUIRED cannot be approved
- Verify invoice exists in database
- Check backend logs for validation details

### Export downloads fail
- Ensure backend dependencies installed (`pandas`, `openpyxl`)
- Check browser download settings
- Verify invoices exist in database

### TypeScript/CSS errors in editor
- CSS `@tailwind` and `@apply` warnings are false positives - they work at runtime
- Run `npm install` to resolve missing module errors
- Restart TypeScript server if needed

## File Structure

```
e:\alepsis/
├── app/                      # Backend
│   ├── api/routes.py        # All API endpoints
│   ├── models/              # ORM & Pydantic schemas
│   ├── services/            # OCR, extraction, export
│   ├── validation/          # Business rules
│   └── database.py          # SQLAlchemy setup
├── frontend/                # Frontend
│   ├── app/
│   │   ├── page.tsx        # Dashboard
│   │   ├── upload/         # Upload page
│   │   ├── invoices/       # List & detail pages
│   │   ├── components/     # Reusable components
│   │   └── lib/api.ts      # API client
│   ├── package.json
│   └── next.config.js
├── invoices.db             # SQLite database
└── requirements.txt        # Python dependencies
```

## Next Steps

- Test with various invoice formats (PDF, JPG, PNG)
- Verify validation logic with edge cases
- Test export with filtered status
- Check mobile responsiveness
- Performance testing with multiple invoices
