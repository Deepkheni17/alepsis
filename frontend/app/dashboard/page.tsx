'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { supabase } from '../../lib/supabase'
import {
  FileText, Upload, Download, CheckCircle2,
  Clock, AlertTriangle, Trash2, Eye, ChevronRight, TrendingUp
} from 'lucide-react'
import { AppSidebar } from '@/components/blocks/app-sidebar'

const API_BASE_URL = '/api'

interface Invoice {
  id: number
  vendor_name: string | null
  invoice_number: string | null
  invoice_date: string | null
  total_amount: number | null
  currency: string | null
  is_valid: boolean
  status: 'PENDING' | 'REVIEW_REQUIRED' | 'APPROVED'
  created_at: string
}

const STATUS_CONFIG = {
  APPROVED: {
    label: 'Approved',
    class: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-400',
    icon: CheckCircle2,
  },
  PENDING: {
    label: 'Pending',
    class: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-400',
    icon: Clock,
  },
  REVIEW_REQUIRED: {
    label: 'Review Required',
    class: 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-400',
    icon: AlertTriangle,
  },
}


function LoadingScreen() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="flex flex-col items-center gap-4">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center animate-pulse">
          <FileText className="w-6 h-6 text-white" />
        </div>
        <p className="text-muted-foreground text-sm">Loading your dashboard…</p>
      </div>
    </div>
  )
}

export default function DashboardPage() {
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [userEmail, setUserEmail] = useState<string>('')
  const router = useRouter()

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const { data: { session }, error: sessionError } = await supabase.auth.getSession()
      if (sessionError) throw sessionError
      if (!session) { router.push('/login'); return }

      setUserEmail(session.user.email || '')
      setLoading(false)
      fetchInvoices(session.access_token).catch(err => {
        console.error('Failed to fetch invoices:', err)
        setError('Failed to load invoices. Please refresh.')
      })
    } catch (err: any) {
      setError(err.message || 'Authentication failed')
      setLoading(false)
      router.push('/login')
    }
  }

  const fetchInvoices = async (accessToken: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/invoices`, {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      })
      if (!response.ok) throw new Error('Failed to fetch invoices')
      const data = await response.json()
      setInvoices(data.invoices || [])
    } catch (err: any) {
      setError(err.message || 'Failed to load invoices')
    }
  }


  const handleExport = async (format: 'csv' | 'xlsx') => {
    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) return
      const response = await fetch(`${API_BASE_URL}/invoices/export?format=${format}`, {
        headers: { 'Authorization': `Bearer ${session.access_token}` }
      })
      if (!response.ok) throw new Error('Export failed')
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `invoices_${Date.now()}.${format}`
      a.click()
    } catch (err: any) {
      alert(err.message || 'Export failed')
    }
  }

  const handleApprove = async (invoiceId: number) => {
    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) return
      const response = await fetch(`${API_BASE_URL}/invoices/${invoiceId}/approve`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${session.access_token}` }
      })
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail?.message || 'Approval failed')
      }
      await fetchInvoices(session.access_token)
    } catch (err: any) {
      alert(err.message || 'Failed to approve invoice')
    }
  }

  const handleDelete = async (invoiceId: number) => {
    if (!confirm('Are you sure you want to delete this invoice?')) return
    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) return
      const response = await fetch(`${API_BASE_URL}/invoices/${invoiceId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${session.access_token}` }
      })
      if (!response.ok) throw new Error('Delete failed')
      await fetchInvoices(session.access_token)
    } catch (err: any) {
      alert(err.message || 'Failed to delete invoice')
    }
  }

  if (loading) return <LoadingScreen />

  const total = invoices.length
  const pending = invoices.filter(inv => inv.status === 'PENDING').length
  const reviewRequired = invoices.filter(inv => inv.status === 'REVIEW_REQUIRED').length
  const approved = invoices.filter(inv => inv.status === 'APPROVED').length

  const stats = [
    { label: 'Total Invoices', value: total, icon: FileText, color: 'from-blue-500 to-blue-600', bg: 'bg-blue-50 dark:bg-blue-950/30', text: 'text-blue-600 dark:text-blue-400' },
    { label: 'Approved', value: approved, icon: CheckCircle2, color: 'from-emerald-500 to-emerald-600', bg: 'bg-emerald-50 dark:bg-emerald-950/30', text: 'text-emerald-600 dark:text-emerald-400' },
    { label: 'Pending', value: pending, icon: Clock, color: 'from-amber-500 to-amber-600', bg: 'bg-amber-50 dark:bg-amber-950/30', text: 'text-amber-600 dark:text-amber-400' },
    { label: 'Review Required', value: reviewRequired, icon: AlertTriangle, color: 'from-orange-500 to-orange-600', bg: 'bg-orange-50 dark:bg-orange-950/30', text: 'text-orange-600 dark:text-orange-400' },
  ]

  return (
    <div className="min-h-screen bg-background flex">
      <AppSidebar userEmail={userEmail} active="dashboard" />

      {/* Main content */}
      <div className="flex-1 lg:ml-64 flex flex-col">
        {/* Top bar */}
        <header className="sticky top-0 z-10 bg-background/80 backdrop-blur-lg border-b border-border px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-foreground">Dashboard</h1>
            <p className="text-xs text-muted-foreground mt-0.5">Welcome back, {userEmail}</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => handleExport('csv')}
              className="hidden sm:flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-muted-foreground hover:text-foreground border border-border rounded-lg hover:bg-muted transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              CSV
            </button>
            <button
              onClick={() => handleExport('xlsx')}
              className="hidden sm:flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-muted-foreground hover:text-foreground border border-border rounded-lg hover:bg-muted transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              Excel
            </button>
            <Link
              href="/upload"
              className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all shadow-sm shadow-blue-500/20"
            >
              <Upload className="w-3.5 h-3.5" />
              Upload
            </Link>
          </div>
        </header>

        <main className="flex-1 p-6 max-w-7xl">
          {/* Error banner */}
          {error && (
            <div className="mb-6 flex items-start gap-3 bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 rounded-xl p-4 text-sm">
              <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />
              {error}
            </div>
          )}

          {/* Stats */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {stats.map((stat) => (
              <div
                key={stat.label}
                className="relative overflow-hidden bg-card border border-border rounded-2xl p-5 shadow-sm hover:shadow-md transition-all duration-300 group hover:-translate-y-0.5"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-xs font-medium text-muted-foreground mb-1">{stat.label}</p>
                    <p className="text-3xl font-bold text-foreground">{stat.value}</p>
                  </div>
                  <div className={`w-10 h-10 rounded-xl ${stat.bg} flex items-center justify-center`}>
                    <stat.icon className={`w-5 h-5 ${stat.text}`} />
                  </div>
                </div>
                <div className={`absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r ${stat.color} opacity-0 group-hover:opacity-100 transition-opacity`} />
              </div>
            ))}
          </div>

          {/* Invoices table */}
          <div className="bg-card border border-border rounded-2xl shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-border flex items-center justify-between">
              <div className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-blue-600" />
                <h2 className="text-sm font-semibold text-foreground">Recent Invoices</h2>
                <span className="text-xs text-muted-foreground bg-muted rounded-full px-2 py-0.5">{total}</span>
              </div>
              <Link
                href="/invoices"
                className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700 font-medium transition-colors"
              >
                View all <ChevronRight className="w-3 h-3" />
              </Link>
            </div>

            {invoices.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-20 gap-4">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/30 flex items-center justify-center">
                  <FileText className="w-8 h-8 text-blue-400" />
                </div>
                <div className="text-center">
                  <p className="text-sm font-medium text-foreground">No invoices yet</p>
                  <p className="text-xs text-muted-foreground mt-1">Upload your first invoice to get started</p>
                </div>
                <Link
                  href="/upload"
                  className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all"
                >
                  <Upload className="w-3.5 h-3.5" />
                  Upload Invoice
                </Link>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="bg-muted/40">
                      <th className="px-6 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">Invoice #</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">Vendor</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">Date</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">Amount</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {invoices.map((invoice) => {
                      const statusCfg = STATUS_CONFIG[invoice.status]
                      const StatusIcon = statusCfg.icon
                      return (
                        <tr key={invoice.id} className="hover:bg-muted/30 transition-colors group">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <Link
                              href={`/invoices/${invoice.id}`}
                              className="text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 flex items-center gap-1 transition-colors"
                            >
                              {invoice.invoice_number || `#${invoice.id}`}
                              <Eye className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                            </Link>
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
                            <div className="flex items-center gap-2">
                              {invoice.status === 'PENDING' && (
                                <button
                                  onClick={() => handleApprove(invoice.id)}
                                  className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/30 hover:bg-emerald-100 dark:hover:bg-emerald-950/50 rounded-lg transition-colors"
                                >
                                  <CheckCircle2 className="w-3 h-3" />
                                  Approve
                                </button>
                              )}
                              <button
                                onClick={() => handleDelete(invoice.id)}
                                className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/30 hover:bg-red-100 dark:hover:bg-red-950/50 rounded-lg transition-colors"
                              >
                                <Trash2 className="w-3 h-3" />
                                Delete
                              </button>
                            </div>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}
