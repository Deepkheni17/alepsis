'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { supabase } from '../../lib/supabase'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'

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
      
      if (sessionError) {
        throw sessionError
      }

      if (!session) {
        router.push('/login')
        return
      }

      setUserEmail(session.user.email || '')
      setLoading(false) // Stop loading to show dashboard immediately
      
      // Fetch invoices in background without blocking UI
      fetchInvoices(session.access_token).catch(err => {
        console.error('Failed to fetch invoices:', err)
        setError('Failed to load invoices. Please refresh the page.')
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
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      })

      if (!response.ok) {
        throw new Error('Failed to fetch invoices')
      }

      const data = await response.json()
      setInvoices(data.invoices || [])
    } catch (err: any) {
      console.error('Fetch invoices error:', err)
      setError(err.message || 'Failed to load invoices')
    }
  }

  const handleLogout = async () => {
    await supabase.auth.signOut()
    router.push('/login')
  }

  const handleExport = async (format: 'csv' | 'xlsx') => {
    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) return

      const response = await fetch(`${API_BASE_URL}/invoices/export?format=${format}`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
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
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail?.message || 'Approval failed')
      }

      // Refresh invoices
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
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      })

      if (!response.ok) throw new Error('Delete failed')

      // Refresh invoices
      await fetchInvoices(session.access_token)
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

  const total = invoices.length
  const pending = invoices.filter(inv => inv.status === 'PENDING').length
  const reviewRequired = invoices.filter(inv => inv.status === 'REVIEW_REQUIRED').length
  const approved = invoices.filter(inv => inv.status === 'APPROVED').length

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-xl font-bold text-gray-900">Invoice Dashboard</h1>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">{userEmail}</span>
              <button
                onClick={handleLogout}
                className="text-sm text-red-600 hover:text-red-700 font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 rounded p-4 mb-6">
            {error}
          </div>
        )}

        <div className="flex gap-4 mb-8">
          <Link
            href="/upload"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium"
          >
            Upload Invoice
          </Link>
          <button
            onClick={() => handleExport('csv')}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 font-medium"
          >
            Export CSV
          </button>
          <button
            onClick={() => handleExport('xlsx')}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 font-medium"
          >
            Export Excel
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-gray-600 text-sm mb-1">Total Invoices</div>
            <div className="text-3xl font-bold">{total}</div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-gray-600 text-sm mb-1">Pending</div>
            <div className="text-3xl font-bold text-yellow-600">{pending}</div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-gray-600 text-sm mb-1">Review Required</div>
            <div className="text-3xl font-bold text-orange-600">{reviewRequired}</div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-gray-600 text-sm mb-1">Approved</div>
            <div className="text-3xl font-bold text-green-600">{approved}</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Invoice #</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Vendor</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {invoices.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                    No invoices found. Upload your first invoice!
                  </td>
                </tr>
              ) : (
                invoices.map((invoice) => (
                  <tr key={invoice.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <Link href={`/invoices/${invoice.id}`} className="text-blue-600 hover:text-blue-800">
                        {invoice.invoice_number || `#${invoice.id}`}
                      </Link>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {invoice.vendor_name || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {invoice.invoice_date || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {invoice.total_amount !== null ? `${invoice.currency || ''} ${invoice.total_amount.toFixed(2)}` : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        invoice.status === 'APPROVED' ? 'bg-green-100 text-green-800' :
                        invoice.status === 'REVIEW_REQUIRED' ? 'bg-orange-100 text-orange-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {invoice.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <div className="flex gap-2">
                        {invoice.status === 'PENDING' && (
                          <button
                            onClick={() => handleApprove(invoice.id)}
                            className="text-green-600 hover:text-green-800 font-medium"
                          >
                            Approve
                          </button>
                        )}
                        <button
                          onClick={() => handleDelete(invoice.id)}
                          className="text-red-600 hover:text-red-800 font-medium"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  )
}
