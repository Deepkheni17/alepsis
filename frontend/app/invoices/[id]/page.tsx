import Link from 'next/link'
import { fetchInvoice } from '../../lib/api'
import ApproveButton from '../../components/ApproveButton'

export default async function InvoiceDetailPage({
  params,
}: {
  params: { id: string }
}) {
  let invoice = null
  let error = null
  
  try {
    invoice = await fetchInvoice(params.id)
  } catch (e) {
    error = e instanceof Error ? e.message : 'Failed to load invoice'
  }
  
  if (error) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-red-50 border border-red-200 text-red-800 rounded p-4 mb-6">
          {error}
        </div>
        <Link href="/invoices" className="btn-secondary">
          ← Back to Invoices
        </Link>
      </div>
    )
  }
  
  if (!invoice) {
    return <div>Loading...</div>
  }
  
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'PENDING':
        return <span className="badge badge-pending">PENDING</span>
      case 'REVIEW_REQUIRED':
        return <span className="badge badge-review">REVIEW REQUIRED</span>
      case 'APPROVED':
        return <span className="badge badge-approved">APPROVED</span>
      default:
        return <span className="badge">{status}</span>
    }
  }
  
  const canApprove = invoice.status !== 'REVIEW_REQUIRED' && invoice.status !== 'APPROVED'
  
  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Invoice #{invoice.id}</h1>
        <Link href="/invoices" className="btn-secondary">
          ← Back to List
        </Link>
      </div>
      
      {/* Status and Actions */}
      <div className="card mb-6 flex justify-between items-center">
        <div>
          <div className="text-sm text-gray-600 mb-1">Status</div>
          <div>{getStatusBadge(invoice.status)}</div>
        </div>
        {canApprove && (
          <ApproveButton invoiceId={invoice.id} />
        )}
        {invoice.status === 'REVIEW_REQUIRED' && (
          <div className="text-sm text-orange-600">
            Cannot approve: Has validation errors
          </div>
        )}
      </div>
      
      {/* Invoice Details */}
      <div className="card mb-6">
        <h2 className="text-xl font-semibold mb-4">Invoice Details</h2>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Vendor Name:</span>
            <div className="font-medium">{invoice.vendor_name || 'N/A'}</div>
          </div>
          <div>
            <span className="text-gray-600">Invoice Number:</span>
            <div className="font-medium">{invoice.invoice_number || 'N/A'}</div>
          </div>
          <div>
            <span className="text-gray-600">Invoice Date:</span>
            <div className="font-medium">{invoice.invoice_date || 'N/A'}</div>
          </div>
          <div>
            <span className="text-gray-600">Currency:</span>
            <div className="font-medium">{invoice.currency || 'N/A'}</div>
          </div>
          <div>
            <span className="text-gray-600">Subtotal:</span>
            <div className="font-medium">
              {invoice.subtotal !== null ? invoice.subtotal.toFixed(2) : 'N/A'}
            </div>
          </div>
          <div>
            <span className="text-gray-600">Tax:</span>
            <div className="font-medium">
              {invoice.tax !== null ? invoice.tax.toFixed(2) : 'N/A'}
            </div>
          </div>
          <div className="col-span-2">
            <span className="text-gray-600">Total Amount:</span>
            <div className="font-bold text-xl">
              {invoice.total_amount !== null ? invoice.total_amount.toFixed(2) : 'N/A'}
            </div>
          </div>
          <div className="col-span-2">
            <span className="text-gray-600">Created At:</span>
            <div className="font-medium">
              {new Date(invoice.created_at).toLocaleString()}
            </div>
          </div>
          <div className="col-span-2">
            <span className="text-gray-600">Valid:</span>
            <div className="font-medium">
              {invoice.is_valid ? (
                <span className="text-green-600">Yes</span>
              ) : (
                <span className="text-red-600">No</span>
              )}
            </div>
          </div>
        </div>
      </div>
      
      {/* Validation Errors */}
      {invoice.validation_errors.length > 0 && (
        <div className="card border-l-4 border-red-500 mb-6">
          <h2 className="text-xl font-semibold mb-3 text-red-800">Validation Errors</h2>
          <ul className="space-y-2">
            {invoice.validation_errors.map((err, idx) => (
              <li key={idx} className="text-sm text-red-600">
                {err}
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {/* Validation Warnings */}
      {invoice.validation_warnings.length > 0 && (
        <div className="card border-l-4 border-yellow-500 mb-6">
          <h2 className="text-xl font-semibold mb-3 text-yellow-800">Validation Warnings</h2>
          <ul className="space-y-2">
            {invoice.validation_warnings.map((warn, idx) => (
              <li key={idx} className="text-sm text-yellow-600">
                {warn}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
