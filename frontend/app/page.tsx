import Link from 'next/link'
import { fetchInvoices, type Invoice } from './lib/api'
import DashboardActions from './components/DashboardActions'

export default async function Home() {
  let invoices: Invoice[] = []
  let error = null
  
  try {
    const data = await fetchInvoices()
    invoices = data.invoices
  } catch (e) {
    error = e instanceof Error ? e.message : 'Failed to load invoices'
  }
  
  // Compute summary
  const total = invoices.length
  const pending = invoices.filter(inv => inv.status === 'PENDING').length
  const reviewRequired = invoices.filter(inv => inv.status === 'REVIEW_REQUIRED').length
  const approved = invoices.filter(inv => inv.status === 'APPROVED').length
  
  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Invoice Processing System</h1>
      
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 rounded p-4 mb-6">
          {error}
        </div>
      )}
      
      {/* Action Buttons - Now using Client Component */}
      <DashboardActions />
      
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="card">
          <div className="text-gray-600 text-sm mb-1">Total Invoices</div>
          <div className="text-3xl font-bold">{total}</div>
        </div>
        
        <div className="card">
          <div className="text-gray-600 text-sm mb-1">Pending</div>
          <div className="text-3xl font-bold text-yellow-600">{pending}</div>
        </div>
        
        <div className="card">
          <div className="text-gray-600 text-sm mb-1">Review Required</div>
          <div className="text-3xl font-bold text-orange-600">{reviewRequired}</div>
        </div>
        
        <div className="card">
          <div className="text-gray-600 text-sm mb-1">Approved</div>
          <div className="text-3xl font-bold text-green-600">{approved}</div>
        </div>
      </div>
      
      {/* Quick Links */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
        <div className="space-y-2">
          <Link href="/invoices" className="block text-blue-600 hover:text-blue-800">
            → View all invoices
          </Link>
          <Link href="/upload" className="block text-blue-600 hover:text-blue-800">
            → Upload new invoice
          </Link>
          {reviewRequired > 0 && (
            <a 
              href="/api/invoices/export?format=csv&status=REVIEW_REQUIRED" 
              className="block text-orange-600 hover:text-orange-800"
            >
              → Export invoices needing review ({reviewRequired})
            </a>
          )}
          {approved > 0 && (
            <a 
              href="/api/invoices/export?format=csv&status=APPROVED" 
              className="block text-green-600 hover:text-green-800"
            >
              → Export approved invoices ({approved})
            </a>
          )}
        </div>
      </div>
    </div>
  )
}
