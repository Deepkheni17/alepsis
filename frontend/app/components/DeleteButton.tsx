'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { deleteInvoice } from '../lib/api'

interface DeleteButtonProps {
  invoiceId: number
}

export default function DeleteButton({ invoiceId }: DeleteButtonProps) {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this invoice? This action cannot be undone.')) {
      return
    }
    
    setLoading(true)
    setError(null)
    
    try {
      await deleteInvoice(invoiceId)
      alert('Invoice deleted successfully!')
      router.push('/invoices') // Redirect to invoice list
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Failed to delete'
      setError(message)
      alert(`Error: ${message}`)
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div>
      <button
        onClick={handleDelete}
        disabled={loading}
        className="text-red-600 hover:text-red-800 px-4 py-2 border border-red-300 rounded hover:bg-red-50 disabled:opacity-50 font-medium"
      >
        {loading ? 'Deleting...' : 'Delete Invoice'}
      </button>
      {error && (
        <div className="text-red-600 text-sm mt-2">{error}</div>
      )}
    </div>
  )
}
