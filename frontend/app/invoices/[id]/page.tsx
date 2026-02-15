'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { fetchInvoice } from '../../../lib/api'
import { supabase } from '../../../lib/supabase'
import type { InvoiceDetail } from '../../../lib/api'

export default function InvoiceDetailPage({
  params,
}: {
  params: { id: string }
}) {
  const router = useRouter()
  const [invoice, setInvoice] = useState<InvoiceDetail | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    loadInvoice()
  }, [params.id])
  
  const loadInvoice = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) {
        router.push('/login')
        return
      }
      
      const data = await fetchInvoice(params.id, session.access_token)
      setInvoice(data)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load invoice')
    } finally {
      setLoading(false)
    }
  }
  
  const handleApprove = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) return
      
      const response = await fetch(`http://localhost:8000/invoices/${params.id}/approve`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail?.message || 'Approval failed')
      }
      
      // Reload invoice
      await loadInvoice()
    } catch (err: any) {
      alert(err.message || 'Failed to approve invoice')
    }
  }
  
  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this invoice?')) return
    
    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) return
      
      const response = await fetch(`http://localhost:8000/invoices/${params.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      })
      
      if (!response.ok) throw new Error('Delete failed')
      
      router.push('/dashboard')
    } catch (err: any) {
      alert(err.message || 'Failed to delete invoice')
    }
  }
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-600">Loading...</div>
      </div>
    )
  }
  
  if (error) {
    return (
      <div className="max-w-4xl mx-auto py-8">
        <div className="bg-red-50 border border-red-200 text-red-800 rounded p-4 mb-6">
          {error}
        </div>
        <Link href="/dashboard" className="inline-block px-4 py-2 bg-gray-200 rounded hover:bg-gray-300">
          ← Back to Dashboard
        </Link>
      </div>
    )
  }
  
  if (!invoice) {
    return <div>No invoice data</div>
  }
  
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'PENDING':
        return <span className="px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800">PENDING</span>
      case 'REVIEW_REQUIRED':
        return <span className="px-2 py-1 text-xs font-medium rounded-full bg-orange-100 text-orange-800">REVIEW REQUIRED</span>
      case 'APPROVED':
        return <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">APPROVED</span>
      default:
        return <span className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800">{status}</span>
    }
  }
  
  const canApprove = invoice.status !== 'REVIEW_REQUIRED' && invoice.status !== 'APPROVED'
  
  return (
    <div className="max-w-4xl mx-auto py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Invoice #{invoice.id}</h1>
        <Link href="/dashboard" className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300">
          ← Back to Dashboard
        </Link>
      </div>
      
      {/* Status and Actions */}
      <div className="bg-white rounded-lg shadow p-6 mb-6 flex justify-between items-center">
        <div>
          <div className="text-sm text-gray-600 mb-1">Status</div>
          <div>{getStatusBadge(invoice.status)}</div>
        </div>
        <div className="flex gap-3">
          {canApprove && (
            <button
              onClick={handleApprove}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              Approve
            </button>
          )}
          {invoice.status === 'REVIEW_REQUIRED' && (
            <div className="text-sm text-orange-600">
              Cannot approve: Has validation errors
            </div>
          )}
          <button
            onClick={handleDelete}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Delete
          </button>
        </div>
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

      {/* Line Items */}
      {invoice.line_items && invoice.line_items.length > 0 && (
        <div className="card mb-6">
          <h2 className="text-xl font-semibold mb-4">Line Items</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left p-3">Product Name</th>
                  <th className="text-right p-3">Quantity</th>
                  <th className="text-right p-3">Unit Price</th>
                  <th className="text-right p-3">Amount</th>
                </tr>
              </thead>
              <tbody>
                {invoice.line_items.map((item, idx) => (
                  <tr key={idx} className="border-b border-gray-100">
                    <td className="p-3">{item.product_name || 'N/A'}</td>
                    <td className="p-3 text-right">
                      {item.quantity !== null ? item.quantity.toFixed(2) : 'N/A'}
                    </td>
                    <td className="p-3 text-right">
                      {item.unit_price !== null 
                        ? `${invoice.currency || ''} ${item.unit_price.toFixed(2)}`
                        : 'N/A'}
                    </td>
                    <td className="p-3 text-right font-medium">
                      {item.amount !== null 
                        ? `${invoice.currency || ''} ${item.amount.toFixed(2)}`
                        : 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Financial Summary */}
      <div className="card mb-6">
        <h2 className="text-xl font-semibold mb-4">Financial Summary</h2>
        <div className="space-y-3 text-sm">
          {/* Subtotal */}
          <div className="flex justify-between items-center pb-2 border-b border-gray-200">
            <span className="text-gray-600">Subtotal:</span>
            <span className="font-medium">
              {invoice.subtotal !== null 
                ? `${invoice.currency || ''} ${invoice.subtotal.toFixed(2)}`
                : 'N/A'}
            </span>
          </div>

          {/* Discount */}
          {(invoice.discount_percentage !== null || invoice.discount_amount !== null) && (
            <div className="flex justify-between items-center pb-2 border-b border-gray-200">
              <span className="text-gray-600">
                Discount
                {invoice.discount_percentage !== null && ` (${invoice.discount_percentage}%)`}:
              </span>
              <span className="font-medium text-red-600">
                {invoice.discount_amount !== null 
                  ? `- ${invoice.currency || ''} ${invoice.discount_amount.toFixed(2)}`
                  : 'N/A'}
              </span>
            </div>
          )}

          {/* Tax Breakdown */}
          <div className="pt-2">
            <div className="text-gray-600 font-medium mb-2">Tax Breakdown:</div>
            
            {/* CGST */}
            {(invoice.cgst_rate !== null || invoice.cgst_amount !== null) && (
              <div className="flex justify-between items-center pl-4 py-1">
                <span className="text-gray-600">
                  CGST (Central Tax)
                  {invoice.cgst_rate !== null && ` @ ${invoice.cgst_rate}%`}:
                </span>
                <span className="font-medium">
                  {invoice.cgst_amount !== null 
                    ? `${invoice.currency || ''} ${invoice.cgst_amount.toFixed(2)}`
                    : 'N/A'}
                </span>
              </div>
            )}

            {/* SGST */}
            {(invoice.sgst_rate !== null || invoice.sgst_amount !== null) && (
              <div className="flex justify-between items-center pl-4 py-1">
                <span className="text-gray-600">
                  SGST (State/UT Tax)
                  {invoice.sgst_rate !== null && ` @ ${invoice.sgst_rate}%`}:
                </span>
                <span className="font-medium">
                  {invoice.sgst_amount !== null 
                    ? `${invoice.currency || ''} ${invoice.sgst_amount.toFixed(2)}`
                    : 'N/A'}
                </span>
              </div>
            )}

            {/* Total Tax */}
            <div className="flex justify-between items-center pb-2 border-b border-gray-200 mt-2">
              <span className="text-gray-600">Total Tax:</span>
              <span className="font-medium">
                {invoice.tax !== null 
                  ? `${invoice.currency || ''} ${invoice.tax.toFixed(2)}`
                  : 'N/A'}
              </span>
            </div>
          </div>

          {/* Grand Total */}
          <div className="flex justify-between items-center pt-2">
            <span className="text-gray-700 font-semibold text-lg">Grand Total:</span>
            <span className="font-bold text-xl text-green-700">
              {invoice.total_amount !== null 
                ? `${invoice.currency || ''} ${invoice.total_amount.toFixed(2)}`
                : 'N/A'}
            </span>
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
