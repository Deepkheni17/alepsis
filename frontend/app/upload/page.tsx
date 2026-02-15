'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { uploadInvoice, type UploadResponse } from '../../lib/api'
import { supabase } from '../../lib/supabase'

export default function UploadPage() {
  const router = useRouter()
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<UploadResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  
  useEffect(() => {
    // Check authentication
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (!session) {
        router.push('/login')
      }
    })
  }, [router])
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!file) {
      setError('Please select a file')
      return
    }
    
    setLoading(true)
    setError(null)
    setResult(null)
    
    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) {
        throw new Error('Not authenticated')
      }
      
      const data = await uploadInvoice(file, session.access_token)
      setResult(data)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Upload failed')
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Upload Invoice</h1>
      
      <form onSubmit={handleSubmit} className="card mb-6">
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">
            Select Invoice File (PDF, JPG, PNG, TIFF)
          </label>
          <input
            type="file"
            accept=".pdf,.jpg,.jpeg,.png,.tiff"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="block w-full text-sm text-gray-900 border border-gray-300 rounded cursor-pointer bg-gray-50 focus:outline-none p-2"
            disabled={loading}
          />
        </div>
        
        <div className="flex gap-3">
          <button
            type="submit"
            disabled={loading || !file}
            className="btn-primary"
          >
            {loading ? 'Processing...' : 'Upload & Process'}
          </button>
          
          {result && (
            <button
              type="button"
              onClick={() => router.push('/invoices')}
              className="btn-secondary"
            >
              View All Invoices
            </button>
          )}
        </div>
      </form>
      
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 rounded p-4 mb-6">
          <strong className="text-lg">Error:</strong>
          <div className="mt-2 whitespace-pre-wrap text-sm">{error}</div>
        </div>
      )}
      
      {result && (
        <div className="space-y-6">
          {/* Processing Status */}
          <div className={`card ${result.processing_success ? 'border-l-4 border-green-500' : 'border-l-4 border-red-500'}`}>
            <h2 className="text-xl font-semibold mb-2">Processing Status</h2>
            <div className="space-y-1 text-sm">
              <div>Processing: <span className={result.processing_success ? 'text-green-600 font-medium' : 'text-red-600 font-medium'}>
                {result.processing_success ? 'Success' : 'Failed'}
              </span></div>
              <div>Validation: <span className={result.invoice_valid ? 'text-green-600 font-medium' : 'text-orange-600 font-medium'}>
                {result.invoice_valid ? 'Passed' : 'Has Issues'}
              </span></div>
              {result.processing_notes && (
                <div className="mt-2 text-gray-600">{result.processing_notes}</div>
              )}
            </div>
          </div>
          
          {/* Extracted Data */}
          {result.extracted_data && (
            <div className="card">
              <h2 className="text-xl font-semibold mb-3">Extracted Data</h2>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Vendor:</span>
                  <div className="font-medium">{result.extracted_data.vendor_name || 'Not found'}</div>
                </div>
                <div>
                  <span className="text-gray-600">Invoice Number:</span>
                  <div className="font-medium">{result.extracted_data.invoice_number || 'Not found'}</div>
                </div>
                <div>
                  <span className="text-gray-600">Date:</span>
                  <div className="font-medium">{result.extracted_data.invoice_date || 'Not found'}</div>
                </div>
                <div>
                  <span className="text-gray-600">Currency:</span>
                  <div className="font-medium">{result.extracted_data.currency || 'Not found'}</div>
                </div>
                <div>
                  <span className="text-gray-600">Subtotal:</span>
                  <div className="font-medium">
                    {result.extracted_data.subtotal !== null ? result.extracted_data.subtotal.toFixed(2) : 'Not found'}
                  </div>
                </div>
                <div>
                  <span className="text-gray-600">Tax:</span>
                  <div className="font-medium">
                    {result.extracted_data.tax !== null ? result.extracted_data.tax.toFixed(2) : 'Not found'}
                  </div>
                </div>
                <div className="col-span-2">
                  <span className="text-gray-600">Total Amount:</span>
                  <div className="font-bold text-lg">
                    {result.extracted_data.total_amount !== null ? result.extracted_data.total_amount.toFixed(2) : 'Not found'}
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Validation Errors */}
          {result.validation.errors.length > 0 && (
            <div className="card border-l-4 border-red-500">
              <h2 className="text-xl font-semibold mb-3 text-red-800">Validation Errors</h2>
              <ul className="space-y-2">
                {result.validation.errors.map((err, idx) => (
                  <li key={idx} className="text-sm">
                    <span className="font-medium text-red-700">{err.field}:</span>{' '}
                    <span className="text-red-600">{err.message}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {/* Validation Warnings */}
          {result.validation.warnings.length > 0 && (
            <div className="card border-l-4 border-yellow-500">
              <h2 className="text-xl font-semibold mb-3 text-yellow-800">Validation Warnings</h2>
              <ul className="space-y-2">
                {result.validation.warnings.map((warn, idx) => (
                  <li key={idx} className="text-sm">
                    <span className="font-medium text-yellow-700">{warn.field}:</span>{' '}
                    <span className="text-yellow-600">{warn.message}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
