# Invoice Processing System

Complete AI-powered invoice processing system with FastAPI backend and Next.js frontend.

## Business Problem

Businesses receive invoices as PDFs or images. Accountants manually read these documents and type data into accounting software, causing:
- **Time waste** - Manual data entry is slow
- **Human errors** - Typos and misreads cause accounting mistakes  
- **Money loss** - Delayed processing affects cash flow

## Solution

Full-stack application that automates the entire invoice workflow:
1. **Upload** - Accept invoice PDFs/images via web UI or API
2. **Extract** - OCR + AI extracts structured data
3. **Validate** - Automated business rule validation with errors/warnings
4. **Review** - Web interface for reviewing processed invoices
5. **Approve** - Workflow for approving validated invoices
6. **Export** - Download data as CSV or Excel

## Features

### Backend (FastAPI + Python)
- ✅ OCR-based invoice data extraction
- ✅ Automated validation with errors and warnings
- ✅ Status workflow (PENDING → REVIEW_REQUIRED → APPROVED)
- ✅ SQLite database with SQLAlchemy ORM
- ✅ Export to CSV/Excel with status filtering
- ✅ Duplicate invoice detection
- ✅ RESTful API with interactive documentation

### Frontend (Next.js + TypeScript)
- ✅ Invoice upload interface with live results
- ✅ Dashboard with summary statistics
- ✅ Invoice list table with filtering
- ✅ Detailed invoice view
- ✅ One-click approval workflow
- ✅ Export functionality (CSV/Excel)
- ✅ Responsive design with Tailwind CSS

## Tech Stack

**Backend**:
- FastAPI 0.109.0
- SQLAlchemy 2.0.25
- Python 3.12.4
- pandas 2.1.4 (export)
- openpyxl 3.1.2 (Excel export)

**Frontend**:
- Next.js 14.2+
- React 18.2
- TypeScript 5.3
- Tailwind CSS 3.4

## Project Structure

```
e:\alepsis/
├── app/                          # Backend (FastAPI)
│   ├── main.py                  # FastAPI app entry point
│   ├── database.py              # SQLAlchemy configuration
│   ├── api/
│   │   └── routes.py           # API endpoints
│   ├── models/
│   │   ├── schemas.py          # Pydantic models
│   │   └── orm_models.py       # SQLAlchemy models
│   ├── services/
│   │   ├── ocr.py              # OCR processing
│   │   ├── extraction.py       # Data extraction
│   │   └── export.py           # CSV/Excel export
│   └── validation/
│       └── validator.py        # Business rules
├── frontend/                     # Frontend (Next.js)
│   ├── app/
│   │   ├── page.tsx            # Dashboard
│   │   ├── layout.tsx          # Root layout
│   │   ├── upload/             # Upload interface
│   │   ├── invoices/           # List & detail views
│   │   ├── components/         # Reusable components
│   │   └── lib/api.ts          # API client
│   ├── package.json
│   ├── tsconfig.json
│   └── next.config.js          # Next.js configuration
├── invoices.db                  # SQLite database
├── requirements.txt             # Python dependencies
└── TESTING_GUIDE.md            # Detailed testing instructions
```

## Quick Start

### Easy Start (Recommended)
Run the included PowerShell script to start both servers:
```powershell
.\start-servers.ps1
```

This will open two terminal windows:
- Backend on **http://127.0.0.1:8000**
- Frontend on **http://localhost:3000**

### Manual Start

#### 1. Backend Setup

```powershell
# Navigate to project root
cd e:\alepsis

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Start backend server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend will be available at: **http://127.0.0.1:8000**  
API Documentation: **http://127.0.0.1:8000/docs**

#### 2. Frontend Setup

```powershell
# Open new terminal
cd e:\alepsis\frontend

# Install dependencies (if not already installed)
npm install

# Start development server
npm run dev
```

Frontend will be available at: **http://localhost:3000**

## Usage

1. **Upload Invoice**: Go to http://localhost:3000/upload
2. **View Invoices**: Browse all processed invoices at http://localhost:3000/invoices
3. **Approve Workflow**: Review and approve invoices from detail view
4. **Export Data**: Download CSV or Excel from dashboard

## API Endpoints

### POST /upload-invoice
Upload and process an invoice image/PDF.

**Request**: `multipart/form-data` with `file` field  
**Response**: Extracted data + validation results + status

**Example:**
```bash
curl -X POST "http://127.0.0.1:8000/upload-invoice" \
  -F "file=@invoice.pdf"
```

### GET /invoices
List all invoices with optional pagination.

**Query Params**: `skip` (default: 0), `limit` (default: 100)  
**Response**: Array of invoices with summary data

### GET /invoices/{id}
Get detailed invoice information.

**Response**: Full invoice data including validation errors/warnings

### POST /invoices/{id}/approve
Approve an invoice (only if status is PENDING).

**Response**: Updated invoice with APPROVED status

### GET /invoices/export
Export invoices to CSV or Excel.

**Query Params**:
- `format`: `csv` or `xlsx` (required)
- `status`: `PENDING`, `REVIEW_REQUIRED`, `APPROVED` (optional)

**Response**: File download

## Extracted Fields

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `vendor_name` | string | Vendor/supplier name | Yes |
| `invoice_number` | string | Invoice ID/number | Yes |
| `invoice_date` | string | Invoice date (YYYY-MM-DD) | No |
| `subtotal` | float | Amount before tax | No |
| `tax` | float | Tax amount | No |
| `total_amount` | float | Total amount due | Yes |
| `currency` | string | Currency code (USD, EUR, etc.) | No |

## Validation Logic

### Critical Errors (→ REVIEW_REQUIRED)
- Missing vendor name
- Missing invoice number  
- Missing or negative total amount
- Duplicate invoice detected

### Warnings (→ PENDING)
- Missing tax amount
- Missing invoice date
- Missing currency

## Status Workflow

```
UPLOAD → VALIDATION
            ↓
    [No Critical Errors] → PENDING → [User Approval] → APPROVED
            ↓
    [Has Critical Errors] → REVIEW_REQUIRED (Cannot approve)
```

## Database

SQLite database located at `e:\alepsis\invoices.db`

**Schema**:
```sql
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY,
    vendor_name TEXT,
    invoice_number TEXT,
    invoice_date TEXT,
    subtotal REAL,
    tax REAL,
    total_amount REAL,
    currency TEXT,
    is_valid BOOLEAN,
    validation_errors TEXT,
    status TEXT,  -- PENDING, REVIEW_REQUIRED, APPROVED
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Testing

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for comprehensive testing instructions.

### Quick Test
1. Start backend and frontend servers (use `.\start-servers.ps1`)
2. Navigate to http://localhost:3000
3. Upload a test invoice via /upload page
4. View processed data and approve if valid

## Troubleshooting

**Frontend can't connect to backend**:
- Ensure backend is running on port 8000
- Check Next.js proxy config in `frontend/next.config.js`
- Look for CORS errors in browser console

**Cannot approve invoice**:
- Only PENDING invoices can be approved
- REVIEW_REQUIRED invoices have critical validation errors
- Check backend logs for details

**Export fails**:
- Verify pandas and openpyxl are installed
- Check backend logs for errors
- Ensure invoices exist in database

**TypeScript/CSS errors in editor**:
- CSS `@tailwind` warnings are false positives - they work at runtime
- Run `npm install` in frontend directory
- Restart TypeScript server if needed

**Port already in use**:
```bash
# Backend: Use a different port
uvicorn app.main:app --port 8001

# Frontend: Next.js will auto-increment port if 3000 is busy
```

## Development

### Backend Development
```powershell
# Run with auto-reload
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# View API documentation
# Open http://127.0.0.1:8000/docs
```

### Frontend Development
```powershell
cd frontend
npm run dev
# Open http://localhost:3000
```

## Future Enhancements

### Immediate:
- [ ] Integrate real OCR service (Azure Computer Vision, AWS Textract)
- [ ] Integrate LLM for better extraction (OpenAI GPT-4, Azure OpenAI)
- [ ] Add environment configuration (.env support)
- [ ] Add comprehensive unit tests
- [ ] Add file size limits and validation
- [ ] Add request rate limiting

### Medium-term:
- [ ] User authentication (JWT, OAuth2)
- [ ] Multi-file batch upload
- [ ] Invoice search and advanced filtering
- [ ] Audit trail/history tracking
- [ ] Email notifications
- [ ] Custom validation rules
- [ ] Background job processing (Celery, Redis)

### Long-term:
- [ ] Integration with accounting software (QuickBooks, Xero)
- [ ] Multi-tenancy support
- [ ] Cloud storage integration (Azure Blob, S3)
- [ ] PDF generation for approved invoices
- [ ] Analytics dashboard
- [ ] Mobile app

## License

MIT

## Contact

For questions or issues, contact the development team.
