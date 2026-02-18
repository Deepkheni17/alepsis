'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { fetchInvoices, Invoice } from '../lib/api'
import { supabase } from '../../lib/supabase'
import InvoiceTable from '../components/InvoiceTable'

export default function InvoicesPage() {
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    loadInvoices()
  }, [])

  const loadInvoices = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession()
      
      if (!session) {
        router.push('/login')
        return
      }

      const data = await fetchInvoices(session.access_token)
      setInvoices(data.invoices)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load invoices')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-600">Loading...</div>
      </div>
    )
  }
  
  return (
    <div className="max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">All Invoices</h1>
        <Link href="/upload" className="btn-primary">
          Upload New Invoice
        </Link>
      </div>
      
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 rounded p-4 mb-6">
          {error}
        </div>
      )}
      
      {invoices.length === 0 && !error ? (
        <div className="card text-center py-12">
          <p className="text-gray-600 mb-4">No invoices found</p>
          <Link href="/upload" className="btn-primary inline-block">
            Upload Your First Invoice
          </Link>
        </div>
      ) : (
        <InvoiceTable invoices={invoices} />
      )}
    </div>
  )
}
