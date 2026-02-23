'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { fetchInvoices, Invoice } from '@/app/lib/api'
import { supabase } from '@/lib/supabase'
import {
  FileText, Upload, CheckCircle2, Clock, AlertTriangle,
  Search, Eye, ChevronRight
} from 'lucide-react'
import { AppSidebar } from '@/components/blocks/app-sidebar'


const STATUS_CONFIG = {
  APPROVED:        { label: 'Approved',         class: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-400', icon: CheckCircle2 },
  PENDING:         { label: 'Pending',          class: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-400',         icon: Clock },
  REVIEW_REQUIRED: { label: 'Review Required',  class: 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-400',     icon: AlertTriangle },
}

export default function InvoicesPage() {
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [filtered, setFiltered] = useState<Invoice[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [userEmail, setUserEmail] = useState('')
  const router = useRouter()

  useEffect(() => { loadInvoices() }, [])

  useEffect(() => {
    const q = search.toLowerCase()
    setFiltered(
      invoices.filter(inv =>
        (inv.vendor_name || '').toLowerCase().includes(q) ||
        (inv.invoice_number || '').toLowerCase().includes(q)
      )
    )
  }, [search, invoices])

  const loadInvoices = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) { router.push('/login'); return }
      setUserEmail(session.user.email || '')
      const data = await fetchInvoices(session.access_token)
      setInvoices(data.invoices)
      setFiltered(data.invoices)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load invoices')
    } finally {
      setLoading(false)
    }
  }


  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center animate-pulse">
            <FileText className="w-6 h-6 text-white" />
          </div>
          <p className="text-muted-foreground text-sm">Loading invoices…</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background flex">
      <AppSidebar userEmail={userEmail} active="invoices" />

      {/* Main */}
      <div className="flex-1 lg:ml-64 flex flex-col">
        <header className="sticky top-0 z-10 bg-background/80 backdrop-blur-lg border-b border-border px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-foreground">All Invoices</h1>
            <p className="text-xs text-muted-foreground mt-0.5">{invoices.length} total</p>
          </div>
          <Link href="/upload" className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all shadow-sm shadow-blue-500/20">
            <Upload className="w-3.5 h-3.5" />
            Upload
          </Link>
        </header>

        <main className="flex-1 p-6">
          {error && (
            <div className="mb-6 flex items-start gap-3 bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 rounded-xl p-4 text-sm">
              <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />
              {error}
            </div>
          )}

          {/* Search */}
          <div className="relative mb-6 max-w-sm">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
            <input
              type="text"
              placeholder="Search by vendor or invoice #…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 bg-card border border-border rounded-xl text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500 transition-all"
            />
          </div>

          {filtered.length === 0 && !error ? (
            <div className="flex flex-col items-center justify-center py-24 gap-4">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/30 flex items-center justify-center">
                <FileText className="w-8 h-8 text-blue-400" />
              </div>
              <div className="text-center">
                <p className="text-sm font-medium text-foreground">
                  {search ? 'No invoices match your search' : 'No invoices yet'}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {search ? 'Try a different search term' : 'Upload your first invoice to get started'}
                </p>
              </div>
              {!search && (
                <Link href="/upload" className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all">
                  <Upload className="w-3.5 h-3.5" /> Upload Invoice
                </Link>
              )}
            </div>
          ) : (
            <div className="bg-card border border-border rounded-2xl shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="bg-muted/40">
                      <th className="px-6 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">Invoice #</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">Vendor</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">Date</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">Amount</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">Details</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {filtered.map((invoice) => {
                      const statusCfg = STATUS_CONFIG[invoice.status as keyof typeof STATUS_CONFIG] || STATUS_CONFIG.PENDING
                      const StatusIcon = statusCfg.icon
                      return (
                        <tr key={invoice.id} className="hover:bg-muted/30 transition-colors group">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="text-sm font-medium text-foreground">
                              {invoice.invoice_number || `#${invoice.id}`}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="text-sm font-medium text-foreground">{invoice.vendor_name || '—'}</span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="text-sm text-muted-foreground">{invoice.invoice_date || '—'}</span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="text-sm font-semibold text-foreground">
                              {invoice.total_amount !== null
                                ? `${invoice.currency || ''} ${invoice.total_amount.toFixed(2)}`
                                : '—'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium ${statusCfg.class}`}>
                              <StatusIcon className="w-3 h-3" />
                              {statusCfg.label}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <Link
                              href={`/invoices/${invoice.id}`}
                              className="inline-flex items-center gap-1 text-xs font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors"
                            >
                              <Eye className="w-3.5 h-3.5" />
                              View
                              <ChevronRight className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                            </Link>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
