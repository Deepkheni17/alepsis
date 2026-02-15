'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { supabase } from '../lib/supabase'

export default function Home() {
  const router = useRouter()
  
  useEffect(() => {
    // Check if logged in and redirect to dashboard
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session) {
        router.push('/dashboard')
      }
    })
  }, [router])
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-4xl mx-auto px-4 text-center">
        <h1 className="text-5xl font-bold mb-6 text-gray-900">
          Invoice Processing System
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          AI-powered invoice extraction and validation with multi-user support
        </p>
        
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-semibold mb-4">Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left">
            <div className="p-4 border border-gray-200 rounded">
              <div className="font-semibold text-blue-600 mb-2">🔐 Secure Authentication</div>
              <p className="text-sm text-gray-600">Email/password and Google OAuth login</p>
            </div>
            <div className="p-4 border border-gray-200 rounded">
              <div className="font-semibold text-blue-600 mb-2">🤖 AI Extraction</div>
              <p className="text-sm text-gray-600">Automatic data extraction from invoices</p>
            </div>
            <div className="p-4 border border-gray-200 rounded">
              <div className="font-semibold text-blue-600 mb-2">✅ Validation</div>
              <p className="text-sm text-gray-600">Smart validation and error detection</p>
            </div>
            <div className="p-4 border border-gray-200 rounded">
              <div className="font-semibold text-blue-600 mb-2">👥 Multi-User</div>
              <p className="text-sm text-gray-600">Isolated data for each user account</p>
            </div>
          </div>
        </div>
        
        <div className="flex gap-4 justify-center">
          <Link
            href="/login"
            className="px-8 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition"
          >
            Sign In
          </Link>
          <Link
            href="/dashboard"
            className="px-8 py-3 bg-white border-2 border-blue-600 text-blue-600 rounded-lg font-semibold hover:bg-blue-50 transition"
          >
            View Dashboard
          </Link>
        </div>
      </div>
    </div>
  )
}
