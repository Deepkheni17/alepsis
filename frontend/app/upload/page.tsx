'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { uploadInvoice, type UploadResponse } from '../lib/api'
import { supabase } from '../../lib/supabase'
import {
  Upload, CheckCircle2, AlertTriangle, AlertCircle,
  ArrowLeft, ArrowRight, FileUp, FileCheck
} from 'lucide-react'
import { AppSidebar } from '@/components/blocks/app-sidebar'

export default function UploadPage() {
  const router = useRouter()
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<UploadResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [userEmail, setUserEmail] = useState<string>('')
  const [dragOver, setDragOver] = useState(false)

  useEffect(() => {
    const checkAuth = async () => {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) { router.push('/login'); return }
      setUserEmail(session.user.email || '')
    }
    checkAuth()
  }, [router])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) { setError('Please select a file'); return }
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) throw new Error('Not authenticated')
      const data = await uploadInvoice(file, session.access_token)
      setResult(data)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Upload failed')
    } finally {
      setLoading(false)
    }
  }

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) setFile(droppedFile)
  }, [])


  return (
    <div className="min-h-screen bg-background flex">
      <AppSidebar userEmail={userEmail} active="upload" />

      {/* Main */}
      <div className="flex-1 lg:ml-64 flex flex-col">
        {/* Header */}
        <header className="sticky top-0 z-10 bg-background/80 backdrop-blur-lg border-b border-border px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link
              href="/dashboard"
              className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Dashboard
            </Link>
            <span className="text-border">/</span>
            <span className="text-sm font-medium text-foreground">Upload Invoice</span>
          </div>
        </header>

        <main className="flex-1 p-6 max-w-3xl">
          {!result ? (
            <>
              <div className="mb-8">
                <h1 className="text-2xl font-bold text-foreground mb-1">Upload Invoice</h1>
                <p className="text-muted-foreground text-sm">
                  Upload a PDF, image or scan — AI will extract all the data automatically.
                </p>
              </div>

              {error && (
                <div className="mb-6 flex items-start gap-3 bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 rounded-xl p-4 text-sm">
                  <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="font-medium">Upload failed</p>
                    <p className="mt-0.5 whitespace-pre-wrap">{error}</p>
                  </div>
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Drop zone */}
                <div
                  className={`relative border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all duration-200 ${
                    dragOver
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/20'
                      : file
                      ? 'border-blue-400 bg-blue-50/50 dark:bg-blue-950/10'
                      : 'border-border hover:border-blue-400 hover:bg-muted/30'
                  }`}
                  onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
                  onDragLeave={() => setDragOver(false)}
                  onDrop={handleDrop}
                  onClick={() => document.getElementById('file-input')?.click()}
                >
                  <input
                    id="file-input"
                    type="file"
                    accept=".pdf,.jpg,.jpeg,.png,.tiff"
                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                    className="hidden"
                    disabled={loading}
                  />
                  <div className="flex flex-col items-center gap-4">
                    <div className={`w-14 h-14 rounded-2xl flex items-center justify-center transition-colors ${
                      file ? 'bg-blue-100 dark:bg-blue-950/40' : 'bg-muted'
                    }`}>
                      {file
                        ? <FileCheck className="w-7 h-7 text-blue-600 dark:text-blue-400" />
                        : <FileUp className="w-7 h-7 text-muted-foreground" />
                      }
                    </div>
                    {file ? (
                      <div>
                        <p className="text-sm font-semibold text-foreground">{file.name}</p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {(file.size / 1024 / 1024).toFixed(2)} MB — click to change
                        </p>
                      </div>
                    ) : (
                      <div>
                        <p className="text-sm font-semibold text-foreground">Drop your invoice here</p>
                        <p className="text-xs text-muted-foreground mt-1">or click to browse · PDF, JPG, PNG, TIFF</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-3">
                  <button
                    type="submit"
                    disabled={loading || !file}
                    className="flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-white bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl hover:from-blue-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-blue-500/50 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm shadow-blue-500/20"
                  >
                    {loading ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        Processing…
                      </>
                    ) : (
                      <>
                        <Upload className="w-4 h-4" />
                        Upload & Process
                      </>
                    )}
                  </button>
                  <Link
                    href="/dashboard"
                    className="px-5 py-2.5 text-sm font-medium text-muted-foreground hover:text-foreground border border-border rounded-xl hover:bg-muted transition-colors"
                  >
                    Cancel
                  </Link>
                </div>
              </form>
            </>
          ) : (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-2xl font-bold text-foreground">Results</h1>
                  <p className="text-muted-foreground text-sm mt-1">Invoice processed successfully</p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => { setResult(null); setFile(null) }}
                    className="px-4 py-2 text-sm font-medium border border-border rounded-xl hover:bg-muted transition-colors text-muted-foreground"
                  >
                    Upload Another
                  </button>
                  <Link
                    href="/dashboard"
                    className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all"
                  >
                    Go to Dashboard <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>

              {/* Processing Status */}
              <div className={`border rounded-2xl p-5 ${
                result.processing_success
                  ? 'bg-emerald-50 dark:bg-emerald-950/20 border-emerald-200 dark:border-emerald-800'
                  : 'bg-red-50 dark:bg-red-950/20 border-red-200 dark:border-red-800'
              }`}>
                <div className="flex items-center gap-3 mb-3">
                  {result.processing_success
                    ? <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                    : <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400" />
                  }
                  <h2 className={`text-sm font-semibold ${
                    result.processing_success ? 'text-emerald-800 dark:text-emerald-300' : 'text-red-800 dark:text-red-300'
                  }`}>
                    {result.processing_success ? 'Processing Successful' : 'Processing Failed'}
                  </h2>
                </div>
                <div className="space-y-1 text-sm ml-8">
                  <div className={result.invoice_valid ? 'text-emerald-700 dark:text-emerald-400' : 'text-orange-600 dark:text-orange-400'}>
                    Validation: {result.invoice_valid ? '✓ Passed' : '⚠ Has Issues'}
                  </div>
                  {result.processing_notes && (
                    <div className="text-muted-foreground mt-1">{result.processing_notes}</div>
                  )}
                </div>
              </div>

              {/* Extracted Data */}
              {result.extracted_data && (
                <div className="bg-card border border-border rounded-2xl overflow-hidden shadow-sm">
                  <div className="px-5 py-4 border-b border-border bg-muted/30">
                    <h2 className="text-sm font-semibold text-foreground">Extracted Data</h2>
                  </div>
                  <div className="p-5 grid grid-cols-2 gap-5 text-sm">
                    {[
                      { label: 'Vendor', value: result.extracted_data.vendor_name },
                      { label: 'Invoice Number', value: result.extracted_data.invoice_number },
                      { label: 'Date', value: result.extracted_data.invoice_date },
                      { label: 'Currency', value: result.extracted_data.currency },
                      { label: 'Subtotal', value: result.extracted_data.subtotal !== null ? result.extracted_data.subtotal.toFixed(2) : null },
                      { label: 'Tax', value: result.extracted_data.tax !== null ? result.extracted_data.tax.toFixed(2) : null },
                    ].map(({ label, value }) => (
                      <div key={label}>
                        <p className="text-xs font-medium text-muted-foreground mb-0.5">{label}</p>
                        <p className="font-medium text-foreground">{value || '—'}</p>
                      </div>
                    ))}
                    <div className="col-span-2 pt-4 mt-1 border-t border-border flex justify-between items-center">
                      <p className="text-sm font-semibold text-foreground">Total Amount</p>
                      <p className="text-xl font-bold text-blue-600 dark:text-blue-400">
                        {result.extracted_data.total_amount !== null ? result.extracted_data.total_amount.toFixed(2) : '—'}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Validation Errors */}
              {result.validation.errors.length > 0 && (
                <div className="bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-800 rounded-2xl overflow-hidden">
                  <div className="px-5 py-4 border-b border-red-200 dark:border-red-800 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-red-600 dark:text-red-400" />
                    <h2 className="text-sm font-semibold text-red-800 dark:text-red-300">
                      Validation Errors ({result.validation.errors.length})
                    </h2>
                  </div>
                  <ul className="p-5 space-y-2">
                    {result.validation.errors.map((err: any, idx: number) => (
                      <li key={idx} className="text-sm text-red-700 dark:text-red-400">
                        <span className="font-medium">{err.field}:</span> {err.message}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Validation Warnings */}
              {result.validation.warnings.length > 0 && (
                <div className="bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 rounded-2xl overflow-hidden">
                  <div className="px-5 py-4 border-b border-amber-200 dark:border-amber-800 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-amber-600 dark:text-amber-400" />
                    <h2 className="text-sm font-semibold text-amber-800 dark:text-amber-300">
                      Validation Warnings ({result.validation.warnings.length})
                    </h2>
                  </div>
                  <ul className="p-5 space-y-2">
                    {result.validation.warnings.map((warn: any, idx: number) => (
                      <li key={idx} className="text-sm text-amber-700 dark:text-amber-400">
                        <span className="font-medium">{warn.field}:</span> {warn.message}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
