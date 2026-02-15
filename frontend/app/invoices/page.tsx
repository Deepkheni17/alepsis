import Link from 'next/link'
import { fetchInvoices } from '../../lib/api'
import InvoiceTable from '../components/InvoiceTable'

export default async function InvoicesPage() {
  let invoices = []
  let error = null
  
  try {
    const data = await fetchInvoices()
    invoices = data.invoices
  } catch (e) {
    error = e instanceof Error ? e.message : 'Failed to load invoices'
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
