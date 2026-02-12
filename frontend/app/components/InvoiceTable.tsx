'use client'

import Link from 'next/link'
import { useState } from 'react'
import { approveInvoice, type Invoice } from '../lib/api'

interface InvoiceTableProps {
  invoices: Invoice[]
}

export default function InvoiceTable({ invoices }: InvoiceTableProps) {
  const [approvingId, setApprovingId] = useState<number | null>(null)
  const [localInvoices, setLocalInvoices] = useState(invoices)
  
  const handleApprove = async (id: number) => {
    if (!confirm('Approve this invoice?')) return
    
    setApprovingId(id)
    try {
      await approveInvoice(id)
      
      // Update local state
      setLocalInvoices(prev =>
        prev.map(inv => inv.id === id ? { ...inv, status: 'APPROVED' as const } : inv)
      )
      
      alert('Invoice approved successfully')
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Failed to approve')
    } finally {
      setApprovingId(null)
    }
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
  
  return (
    <div className="card overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200">
            <th className="text-left p-3">ID</th>
            <th className="text-left p-3">Vendor</th>
            <th className="text-left p-3">Invoice #</th>
            <th className="text-left p-3">Date</th>
            <th className="text-right p-3">Total</th>
            <th className="text-left p-3">Status</th>
            <th className="text-left p-3">Created</th>
            <th className="text-center p-3">Actions</th>
          </tr>
        </thead>
        <tbody>
          {localInvoices.map((invoice) => (
            <tr key={invoice.id} className="border-b border-gray-100 hover:bg-gray-50">
              <td className="p-3">{invoice.id}</td>
              <td className="p-3">{invoice.vendor_name || 'N/A'}</td>
              <td className="p-3">{invoice.invoice_number || 'N/A'}</td>
              <td className="p-3">{invoice.invoice_date || 'N/A'}</td>
              <td className="p-3 text-right">
                {invoice.total_amount !== null
                  ? `${invoice.currency || ''} ${invoice.total_amount.toFixed(2)}`
                  : 'N/A'}
              </td>
              <td className="p-3">{getStatusBadge(invoice.status)}</td>
              <td className="p-3 text-xs text-gray-600">
                {new Date(invoice.created_at).toLocaleDateString()}
              </td>
              <td className="p-3">
                <div className="flex gap-2 justify-center">
                  <Link
                    href={`/invoices/${invoice.id}`}
                    className="text-blue-600 hover:text-blue-800 text-xs font-medium"
                  >
                    View
                  </Link>
                  {invoice.status !== 'APPROVED' && invoice.status !== 'REVIEW_REQUIRED' && (
                    <button
                      onClick={() => handleApprove(invoice.id)}
                      disabled={approvingId === invoice.id}
                      className="btn-success text-xs px-2 py-1"
                    >
                      {approvingId === invoice.id ? 'Approving...' : 'Approve'}
                    </button>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      
      {localInvoices.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No invoices found
        </div>
      )}
    </div>
  )
}
