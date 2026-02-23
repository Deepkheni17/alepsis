/**
 * API client for backend communication
 *
 * All requests go through the Next.js /api rewrite proxy defined in next.config.js.
 * This eliminates CORS issues — the browser sees same-origin requests and
 * Next.js forwards them to the actual backend server.
 *
 * next.config.js rewrite: /api/:path* → http://127.0.0.1:8000/:path*
 */

const getBaseUrl = () => '/api'

export interface LineItem {
  product_name: string | null
  quantity: number | null
  unit_price: number | null
  amount: number | null
}

export interface Invoice {
  id: number
  vendor_name: string | null
  invoice_number: string | null
  invoice_date: string | null
  subtotal: number | null
  tax: number | null
  total_amount: number | null
  currency: string | null
  is_valid: boolean
  status: 'PENDING' | 'REVIEW_REQUIRED' | 'APPROVED'
  created_at: string
}

export interface InvoiceDetail extends Invoice {
  line_items: LineItem[]
  discount_percentage: number | null
  discount_amount: number | null
  cgst_rate: number | null
  cgst_amount: number | null
  sgst_rate: number | null
  sgst_amount: number | null
  validation_errors: string[]
  validation_warnings: string[]
}

export interface InvoiceListResponse {
  count: number
  invoices: Invoice[]
}

export interface UploadResponse {
  success: boolean
  processing_success: boolean
  invoice_valid: boolean
  extracted_data: {
    vendor_name: string | null
    invoice_number: string | null
    invoice_date: string | null
    subtotal: number | null
    tax: number | null
    total_amount: number | null
    currency: string | null
  } | null
  validation: {
    is_valid: boolean
    errors: Array<{ field: string; message: string; severity: string }>
    warnings: Array<{ field: string; message: string; severity: string }>
  }
  processing_notes: string | null
}

export interface ApprovalResponse {
  id: number
  status: string
  message: string
}

/**
 * Fetch all invoices
 */
export async function fetchInvoices(accessToken?: string): Promise<InvoiceListResponse> {
  const headers: HeadersInit = {}
  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`
  }
  
  const res = await fetch(`${getBaseUrl()}/invoices`, {
    headers,
    cache: 'no-store'
  })
  
  if (!res.ok) {
    throw new Error('Failed to fetch invoices')
  }
  
  return res.json()
}

/**
 * Fetch single invoice by ID
 */
export async function fetchInvoice(id: string, accessToken?: string): Promise<InvoiceDetail> {
  const headers: HeadersInit = {}
  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`
  }
  
  const res = await fetch(`${getBaseUrl()}/invoices/${id}`, {
    headers,
    cache: 'no-store'
  })
  
  if (!res.ok) {
    if (res.status === 404) {
      throw new Error('Invoice not found')
    }
    throw new Error('Failed to fetch invoice')
  }
  
  return res.json()
}

/**
 * Upload invoice file
 */
export async function uploadInvoice(file: File, accessToken?: string): Promise<UploadResponse> {
  const formData = new FormData()
  formData.append('file', file)
  
  const headers: HeadersInit = {}
  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`
  }
  
  const res = await fetch(`${getBaseUrl()}/upload-invoice`, {
    method: 'POST',
    headers,
    body: formData,
  })
  
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: { message: 'Upload failed' } }))
    // Extract detailed error information from the backend response
    if (error.detail) {
      const detail = error.detail
      const errorMessage = detail.message || 'Upload failed'
      const instructions = detail.details?.instructions || ''
      throw new Error(instructions ? `${errorMessage}\n\n${instructions}` : errorMessage)
    }
    throw new Error(error.message || 'Upload failed')
  }
  
  return res.json()
}

/**
 * Approve invoice
 */
export async function approveInvoice(id: number): Promise<ApprovalResponse> {
  const res = await fetch(`${getBaseUrl()}/invoices/${id}/approve`, {
    method: 'POST',
  })
  
  if (!res.ok) {
    const error = await res.json().catch(() => ({ message: 'Approval failed' }))
    throw new Error(error.message || 'Approval failed')
  }
  
  return res.json()
}

/**
 * Delete invoice
 */
export async function deleteInvoice(id: number): Promise<{ success: boolean; message: string }> {
  const res = await fetch(`${getBaseUrl()}/invoices/${id}`, {
    method: 'DELETE',
  })
  
  if (!res.ok) {
    const error = await res.json().catch(() => ({ message: 'Delete failed' }))
    throw new Error(error.message || 'Delete failed')
  }
  
  return res.json()
}

/**
 * Download export file
 */
export function downloadExport(format: 'csv' | 'xlsx' = 'csv', status?: string) {
  const params = new URLSearchParams({ format })
  if (status) {
    params.append('status', status)
  }
  
  window.location.href = `${getBaseUrl()}/invoices/export?${params.toString()}`
}
