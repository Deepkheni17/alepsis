# Invoice Processing System - Frontend

Next.js 14 frontend for the AI Invoice Processing backend.

## Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start development server:
```bash
npm run dev
```

3. Open http://localhost:3000

## Features

- **Dashboard**: View summary stats and quick actions
- **Upload**: Upload and process invoices
- **Invoice List**: View all invoices with filtering
- **Invoice Detail**: View detailed invoice information
- **Approval Workflow**: Approve invoices that pass validation
- **Export**: Download invoices as CSV or Excel

## Tech Stack

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Fetch API for backend communication

## Backend Connection

The frontend connects to the FastAPI backend running on `http://127.0.0.1:8000`.
API calls are proxied through Next.js rewrites (configured in `next.config.js`).

## Project Structure

```
app/
  page.tsx              # Dashboard
  upload/page.tsx       # Upload page
  invoices/page.tsx     # Invoice list
  invoices/[id]/page.tsx # Invoice detail
  components/
    InvoiceTable.tsx    # Reusable table component
    ApproveButton.tsx   # Approval button component
  lib/
    api.ts              # API client functions
```

## Development

- Run backend: `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`
- Run frontend: `npm run dev` (in frontend directory)
- Access frontend: http://localhost:3000
- Access backend API docs: http://127.0.0.1:8000/docs
