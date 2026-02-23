'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { fetchInvoice } from '@/app/lib/api'
import { supabase } from '@/lib/supabase'
import type { InvoiceDetail } from '@/app/lib/api'
import {
  FileText, ArrowLeft, CheckCircle2, Clock, AlertTriangle,
  Trash2, Upload, AlertCircle
} from 'lucide-react'
import { AppSidebar } from '@/components/blocks/app-sidebar'

const API_BASE_URL = '/api'


function DetailRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-xs font-medium text-muted-foreground">{label}</span>
      <span className="text-sm font-semibold text-foreground">{value || '—'}</span>
    </div>
  )
}

export default function InvoiceDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const [invoice, setInvoice] = useState<InvoiceDetail | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [userEmail, setUserEmail] = useState('')

  useEffect(() => { loadInvoice() }, [params.id])

  const loadInvoice = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) { router.push('/login'); return }
      setUserEmail(session.user.email || '')
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
      const response = await fetch(`${API_BASE_URL}/invoices/${params.id}/approve`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${session.access_token}` }
      })
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail?.message || 'Approval failed')
      }
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
      const response = await fetch(`${API_BASE_URL}/invoices/${params.id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${session.access_token}` }
      })
      if (!response.ok) throw new Error('Delete failed')
      router.push('/dashboard')
    } catch (err: any) {
      alert(err.message || 'Failed to delete invoice')
    }
  }


  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'APPROVED': return { label: 'Approved', class: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-400', icon: CheckCircle2 }
      case 'REVIEW_REQUIRED': return { label: 'Review Required', class: 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-400', icon: AlertTriangle }
      default: return { label: 'Pending', class: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-400', icon: Clock }
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center animate-pulse">
            <FileText className="w-6 h-6 text-white" />
          </div>
          <p className="text-muted-foreground text-sm">Loading invoice…</p>
        </div>
      </div>
    )
  }

  if (error || !invoice) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background p-6">
        <div className="max-w-sm w-full text-center">
          <div className="w-16 h-16 bg-red-50 dark:bg-red-950/30 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-8 h-8 text-red-500" />
          </div>
          <h2 className="text-lg font-bold text-foreground mb-2">Failed to load invoice</h2>
          <p className="text-sm text-muted-foreground mb-6">{error || 'No invoice data found.'}</p>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Dashboard
          </Link>
        </div>
      </div>
    )
  }

  const statusCfg = getStatusConfig(invoice.status)
  const StatusIcon = statusCfg.icon
  const canApprove = invoice.status !== 'REVIEW_REQUIRED' && invoice.status !== 'APPROVED'

  return (
    <div className="min-h-screen bg-background flex">
      <AppSidebar userEmail={userEmail} active="invoices" />

      {/* Main */}
      <div className="flex-1 lg:ml-64 flex flex-col">
        {/* Header */}
        <header className="sticky top-0 z-10 bg-background/80 backdrop-blur-lg border-b border-border px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href="/invoices" className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors">
              <ArrowLeft className="w-4 h-4" /> Invoices
            </Link>
            <span className="text-border">/</span>
            <span className="text-sm font-medium text-foreground">
              {invoice.invoice_number || `Invoice #${invoice.id}`}
            </span>
          </div>
          {/* Actions */}
          <div className="flex items-center gap-2">
            {canApprove && (
              <button
                onClick={handleApprove}
                className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-emerald-500 to-emerald-600 rounded-lg hover:from-emerald-600 hover:to-emerald-700 transition-all shadow-sm"
              >
                <CheckCircle2 className="w-3.5 h-3.5" /> Approve
              </button>
            )}
            {invoice.status === 'REVIEW_REQUIRED' && (
              <span className="text-xs text-orange-600 dark:text-orange-400 font-medium">Cannot approve: has validation errors</span>
            )}
            <button
              onClick={handleDelete}
              className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-red-600 dark:text-red-400 border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950/20 hover:bg-red-100 dark:hover:bg-red-950/40 rounded-lg transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" /> Delete
            </button>
          </div>
        </header>

        <main className="flex-1 p-6 max-w-5xl space-y-6">
          {/* Status banner */}
          <div className="bg-card border border-border rounded-2xl p-5 flex items-center justify-between shadow-sm">
            <div>
              <p className="text-xs font-medium text-muted-foreground mb-1.5">Status</p>
              <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium ${statusCfg.class}`}>
                <StatusIcon className="w-3.5 h-3.5" />
                {statusCfg.label}
              </span>
            </div>
            <div className="text-right">
              <p className="text-xs font-medium text-muted-foreground mb-1">Validation</p>
              <span className={`text-sm font-semibold ${invoice.is_valid ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'}`}>
                {invoice.is_valid ? '✓ Valid' : '✗ Invalid'}
              </span>
            </div>
          </div>

          {/* Invoice Details */}
          <div className="bg-card border border-border rounded-2xl overflow-hidden shadow-sm">
            <div className="px-6 py-4 border-b border-border bg-muted/30">
              <h2 className="text-sm font-semibold text-foreground">Invoice Details</h2>
            </div>
            <div className="p-6 grid grid-cols-2 md:grid-cols-3 gap-6">
              <DetailRow label="Vendor Name" value={invoice.vendor_name} />
              <DetailRow label="Invoice Number" value={invoice.invoice_number} />
              <DetailRow label="Invoice Date" value={invoice.invoice_date} />
              <DetailRow label="Currency" value={invoice.currency} />
              <DetailRow
                label="Created At"
                value={new Date(invoice.created_at).toLocaleString()}
              />
            </div>
          </div>

          {/* Line Items */}
          {invoice.line_items && invoice.line_items.length > 0 && (
            <div className="bg-card border border-border rounded-2xl overflow-hidden shadow-sm">
              <div className="px-6 py-4 border-b border-border bg-muted/30">
                <h2 className="text-sm font-semibold text-foreground">
                  Line Items <span className="text-muted-foreground font-normal ml-1">({invoice.line_items.length})</span>
                </h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-muted/20">
                      <th className="px-6 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">Product</th>
                      <th className="px-6 py-3 text-right text-xs font-semibold text-muted-foreground uppercase tracking-wider">Qty</th>
                      <th className="px-6 py-3 text-right text-xs font-semibold text-muted-foreground uppercase tracking-wider">Unit Price</th>
                      <th className="px-6 py-3 text-right text-xs font-semibold text-muted-foreground uppercase tracking-wider">Amount</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {invoice.line_items.map((item, idx) => (
                      <tr key={idx} className="hover:bg-muted/20 transition-colors">
                        <td className="px-6 py-4 text-foreground font-medium">{item.product_name || '—'}</td>
                        <td className="px-6 py-4 text-right text-muted-foreground">
                          {item.quantity !== null ? item.quantity.toFixed(2) : '—'}
                        </td>
                        <td className="px-6 py-4 text-right text-muted-foreground">
                          {item.unit_price !== null ? `${invoice.currency || ''} ${item.unit_price.toFixed(2)}` : '—'}
                        </td>
                        <td className="px-6 py-4 text-right font-semibold text-foreground">
                          {item.amount !== null ? `${invoice.currency || ''} ${item.amount.toFixed(2)}` : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Financial Summary */}
          <div className="bg-card border border-border rounded-2xl overflow-hidden shadow-sm">
            <div className="px-6 py-4 border-b border-border bg-muted/30">
              <h2 className="text-sm font-semibold text-foreground">Financial Summary</h2>
            </div>
            <div className="p-6 space-y-4 max-w-md ml-auto">
              {/* Subtotal */}
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Subtotal</span>
                <span className="font-medium text-foreground">
                  {invoice.subtotal !== null ? `${invoice.currency || ''} ${invoice.subtotal.toFixed(2)}` : '—'}
                </span>
              </div>

              {/* Discount */}
              {(invoice.discount_percentage !== null || invoice.discount_amount !== null) && (
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">
                    Discount{invoice.discount_percentage !== null ? ` (${invoice.discount_percentage}%)` : ''}
                  </span>
                  <span className="font-medium text-red-600 dark:text-red-400">
                    {invoice.discount_amount !== null ? `− ${invoice.currency || ''} ${invoice.discount_amount.toFixed(2)}` : '—'}
                  </span>
                </div>
              )}

              {/* CGST */}
              {(invoice.cgst_rate !== null || invoice.cgst_amount !== null) && (
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">CGST{invoice.cgst_rate !== null ? ` @ ${invoice.cgst_rate}%` : ''}</span>
                  <span className="font-medium text-foreground">
                    {invoice.cgst_amount !== null ? `${invoice.currency || ''} ${invoice.cgst_amount.toFixed(2)}` : '—'}
                  </span>
                </div>
              )}

              {/* SGST */}
              {(invoice.sgst_rate !== null || invoice.sgst_amount !== null) && (
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">SGST{invoice.sgst_rate !== null ? ` @ ${invoice.sgst_rate}%` : ''}</span>
                  <span className="font-medium text-foreground">
                    {invoice.sgst_amount !== null ? `${invoice.currency || ''} ${invoice.sgst_amount.toFixed(2)}` : '—'}
                  </span>
                </div>
              )}

              {/* Total Tax */}
              <div className="flex justify-between text-sm border-t border-border pt-4">
                <span className="text-muted-foreground">Total Tax</span>
                <span className="font-medium text-foreground">
                  {invoice.tax !== null ? `${invoice.currency || ''} ${invoice.tax.toFixed(2)}` : '—'}
                </span>
              </div>

              {/* Grand Total */}
              <div className="flex justify-between items-center bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/30 border border-blue-100 dark:border-blue-900 rounded-xl px-4 py-3">
                <span className="text-sm font-semibold text-foreground">Grand Total</span>
                <span className="text-xl font-bold text-blue-600 dark:text-blue-400">
                  {invoice.total_amount !== null
                    ? `${invoice.currency || ''} ${invoice.total_amount.toFixed(2)}`
                    : '—'}
                </span>
              </div>
            </div>
          </div>

          {/* Validation Errors */}
          {invoice.validation_errors.length > 0 && (
            <div className="bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-800 rounded-2xl overflow-hidden">
              <div className="px-6 py-4 border-b border-red-200 dark:border-red-800 flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-red-600 dark:text-red-400" />
                <h2 className="text-sm font-semibold text-red-800 dark:text-red-300">
                  Validation Errors ({invoice.validation_errors.length})
                </h2>
              </div>
              <ul className="p-6 space-y-2">
                {invoice.validation_errors.map((err, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm text-red-700 dark:text-red-400">
                    <span className="mt-1 w-1.5 h-1.5 rounded-full bg-red-500 flex-shrink-0" />
                    {err}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Validation Warnings */}
          {invoice.validation_warnings.length > 0 && (
            <div className="bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 rounded-2xl overflow-hidden">
              <div className="px-6 py-4 border-b border-amber-200 dark:border-amber-800 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-600 dark:text-amber-400" />
                <h2 className="text-sm font-semibold text-amber-800 dark:text-amber-300">
                  Validation Warnings ({invoice.validation_warnings.length})
                </h2>
              </div>
              <ul className="p-6 space-y-2">
                {invoice.validation_warnings.map((warn, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm text-amber-700 dark:text-amber-400">
                    <span className="mt-1 w-1.5 h-1.5 rounded-full bg-amber-500 flex-shrink-0" />
                    {warn}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
