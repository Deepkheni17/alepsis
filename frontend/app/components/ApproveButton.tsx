'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { approveInvoice } from '../lib/api'

interface ApproveButtonProps {
  invoiceId: number
}

export default function ApproveButton({ invoiceId }: ApproveButtonProps) {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const handleApprove = async () => {
    if (!confirm('Are you sure you want to approve this invoice?')) {
      return
    }
    
    setLoading(true)
    setError(null)
    
    try {
      await approveInvoice(invoiceId)
      alert('Invoice approved successfully!')
      router.refresh() // Refresh server component data
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Failed to approve'
      setError(message)
      alert(`Error: ${message}`)
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div>
      <button
        onClick={handleApprove}
        disabled={loading}
        className="btn-success"
      >
        {loading ? 'Approving...' : 'Approve Invoice'}
      </button>
      {error && (
        <div className="text-red-600 text-sm mt-2">{error}</div>
      )}
    </div>
  )
}
