'use client'

import Link from 'next/link'

export default function DashboardActions() {
  const handleExport = (format: 'csv' | 'xlsx') => {
    if (typeof window !== 'undefined') {
      window.location.href = `/api/invoices/export?format=${format}`
    }
  }
  
  return (
    <div className="flex gap-4 mb-8">
      <Link href="/upload" className="btn-primary">
        Upload Invoice
      </Link>
      <button 
        onClick={() => handleExport('csv')}
        className="btn-secondary"
      >
        Export CSV
      </button>
      <button 
        onClick={() => handleExport('xlsx')}
        className="btn-secondary"
      >
        Export Excel
      </button>
    </div>
  )
}
