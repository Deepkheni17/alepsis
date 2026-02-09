# AI Invoice Processing Backend (MVP)

Production-ready backend that converts invoice PDFs/images into structured JSON data using AI.

## Business Problem

Businesses receive invoices as PDFs or images. Accountants manually read these documents and type data into accounting software, causing:
- **Time waste** - Manual data entry is slow
- **Human errors** - Typos and misreads cause accounting mistakes  
- **Money loss** - Delayed processing affects cash flow

## Solution

This backend automates invoice data extraction:
1. Accept invoice PDFs/images via API
2. Extract text using OCR (mocked in MVP)
3. Extract structured data using AI (pattern-based in MVP, LLM-ready)
4. Validate extracted data
5. Return clean, predictable JSON

## Tech Stack

- **Language:** Python 3.10+
- **Framework:** FastAPI
- **Architecture:** Monolithic backend (web + AI together)
- **AI:** LLM-ready extraction (currently pattern-based for MVP)
- **Storage:** In-memory (no database in MVP)

## Project Structure

```
alepsis/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py        # API endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ocr.py          # OCR service (mocked)
│   │   └── extraction.py   # AI extraction logic
│   ├── validation/
│   │   ├── __init__.py
│   │   └── validator.py    # Business validation logic
│   └── models/
│       ├── __init__.py
│       └── schemas.py      # Pydantic models
├── requirements.txt
└── README.md
```

## Installation

### Prerequisites
- Python 3.10 or higher
- pip

### Setup

1. **Clone or navigate to the project:**
   ```bash
   cd e:\alepsis
   ```

2. **Create virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Development Mode
```bash
uvicorn app.main:app --reload
```

The API will be available at: `http://127.0.0.1:8000`

### Production Mode (example)
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once running, access:
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

## API Endpoints

### 1. Upload Invoice
**Endpoint:** `POST /upload-invoice`

**Description:** Upload an invoice file (PDF or image) and get structured data.

**Supported Formats:** PDF, JPG, JPEG, PNG, TIFF

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/upload-invoice" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@invoice.pdf"
```

**Response (Success):**
```json
{
  "success": true,
  "extracted_data": {
    "vendor_name": "ABC Corporation",
    "invoice_number": "INV-2024-001234",
    "invoice_date": "2024-01-15",
    "subtotal": 3000.0,
    "tax": 255.0,
    "total_amount": 3255.0,
    "currency": "USD"
  },
  "validation": {
    "is_valid": true,
    "errors": [],
    "warnings": []
  },
  "processing_notes": null
}
```

**Response (With Validation Errors):**
```json
{
  "success": false,
  "extracted_data": {
    "vendor_name": "ABC Corporation",
    "invoice_number": null,
    "invoice_date": "2024-01-15",
    "subtotal": 3000.0,
    "tax": 250.0,
    "total_amount": 3255.0,
    "currency": "USD"
  },
  "validation": {
    "is_valid": false,
    "errors": [
      {
        "field": "invoice_number",
        "message": "Invoice number is missing but required for processing",
        "severity": "error"
      },
      {
        "field": "total_amount",
        "message": "Math error: Subtotal (3000.00) + Tax (250.00) = 3250.00, but Total is 3255.00. Difference: 5.00",
        "severity": "error"
      }
    ],
    "warnings": []
  },
  "processing_notes": "Found 2 validation errors"
}
```

### 2. Health Check
**Endpoint:** `GET /health`

**Description:** Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "AI Invoice Processing Backend",
  "version": "1.0.0"
}
```

## Extracted Fields

The AI extraction service extracts the following fields:

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `vendor_name` | string | Vendor/supplier name | Yes |
| `invoice_number` | string | Invoice ID/number | Yes |
| `invoice_date` | string | Invoice date (YYYY-MM-DD) | No |
| `subtotal` | float | Amount before tax | No |
| `tax` | float | Tax amount | No |
| `total_amount` | float | Total amount due | Yes |
| `currency` | string | Currency code (USD, EUR, etc.) | No |

## Validation Rules

1. **Required Fields:** vendor_name, invoice_number, total_amount must be present
2. **Mathematical Consistency:** If subtotal and tax are present, they must sum to total_amount (within 1 cent tolerance)
3. **Data Quality Warnings:** Flags missing dates, unusual amounts, negative values

## Testing the API

### Using cURL:
```bash
# Create a test file or use an existing invoice
curl -X POST "http://127.0.0.1:8000/upload-invoice" \
  -F "file=@test_invoice.pdf"
```

### Using Python:
```python
import requests

url = "http://127.0.0.1:8000/upload-invoice"
files = {"file": open("invoice.pdf", "rb")}

response = requests.post(url, files=files)
print(response.json())
```

### Using the Swagger UI:
1. Navigate to http://127.0.0.1:8000/docs
2. Click on "POST /upload-invoice"
3. Click "Try it out"
4. Upload a file
5. Click "Execute"

## Next Steps / Future Enhancements

### Immediate (Production Ready):
- [ ] Integrate real OCR service (Azure Computer Vision, AWS Textract, etc.)
- [ ] Integrate real LLM (OpenAI GPT-4, Azure OpenAI, Claude, etc.)
- [ ] Add environment configuration (.env file support)
- [ ] Add comprehensive unit tests
- [ ] Add logging to file instead of just console
- [ ] Add request rate limiting
- [ ] Add file size validation

### Medium-term:
- [ ] Add database (PostgreSQL) for storing processed invoices
- [ ] Add authentication/authorization (API keys, OAuth2)
- [ ] Add background job processing (Celery, Redis Queue)
- [ ] Add support for multi-page invoices
- [ ] Add invoice history and search
- [ ] Add webhook support for async processing

### Long-term:
- [ ] Frontend integration (Next.js, React)
- [ ] Multi-tenancy support
- [ ] Integration with accounting software (QuickBooks, Xero, etc.)
- [ ] Custom field extraction (user-defined fields)
- [ ] Batch processing
- [ ] Analytics dashboard

## Architecture Notes

### Separation of Concerns:
- **`api/`** - HTTP layer, request/response handling
- **`services/`** - Business logic, AI processing
- **`validation/`** - Data validation rules
- **`models/`** - Data structures and schemas

### Design Principles:
- **Fail safely, never silently** - Errors are flagged but don't crash the API
- **Predictable responses** - Consistent JSON structure
- **Easy to extend** - Clean interfaces for adding features
- **Production-ready** - Proper logging, error handling, documentation

## Troubleshooting

### Port already in use:
```bash
# Use a different port
uvicorn app.main:app --port 8001
```

### Import errors:
```bash
# Make sure you're in the project root
cd e:\alepsis

# Make sure dependencies are installed
pip install -r requirements.txt
```

### File upload errors:
- Ensure file is not corrupted
- Check file size (default FastAPI limit is 1MB for small files)
- Verify file extension is supported (.pdf, .jpg, .png, etc.)

## License

This is an MVP project. Add your license here.

## Contact

For questions or issues, contact the development team.
