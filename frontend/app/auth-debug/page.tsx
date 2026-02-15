'use client'

import { useEffect, useState } from 'react'
import { supabase } from '../../lib/supabase'

export default function AuthDebug() {
  const [session, setSession] = useState<any>(null)
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    const { data: { session }, error } = await supabase.auth.getSession()
    
    console.log('Session:', session)
    console.log('Error:', error)
    
    if (session) {
      setSession(session)
      setUser(session.user)
    }
    
    setLoading(false)
  }

  const testSignIn = async () => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email: 'deepkheni07@gmail.com',
      password: 'Deep@3164'
    })
    
    console.log('Sign in result:', data, error)
    alert(error ? `Error: ${error.message}` : 'Success! Check console for details')
    checkAuth()
  }

  if (loading) return <div className="p-8">Loading...</div>

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Auth Debug Page</h1>
      
      <div className="space-y-4">
        <div className="border p-4 rounded">
          <h2 className="font-bold mb-2">Session Status</h2>
          <p className={session ? 'text-green-600' : 'text-red-600'}>
            {session ? '✅ Authenticated' : '❌ Not authenticated'}
          </p>
        </div>

        {user && (
          <div className="border p-4 rounded">
            <h2 className="font-bold mb-2">User Info</h2>
            <pre className="bg-gray-100 p-2 rounded text-sm overflow-auto">
              {JSON.stringify(user, null, 2)}
            </pre>
          </div>
        )}

        {session && (
          <div className="border p-4 rounded">
            <h2 className="font-bold mb-2">Session Info</h2>
            <pre className="bg-gray-100 p-2 rounded text-sm overflow-auto">
              {JSON.stringify({
                access_token: session.access_token.substring(0, 20) + '...',
                expires_at: new Date(session.expires_at * 1000).toLocaleString(),
                user_email: session.user.email
              }, null, 2)}
            </pre>
          </div>
        )}

        <div className="border p-4 rounded">
          <h2 className="font-bold mb-2">Actions</h2>
          <div className="space-x-2">
            <button
              onClick={testSignIn}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Test Sign In
            </button>
            <button
              onClick={checkAuth}
              className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
            >
              Refresh Session
            </button>
            <button
              onClick={() => supabase.auth.signOut().then(() => checkAuth())}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Sign Out
            </button>
          </div>
        </div>

        <div className="border p-4 rounded">
          <h2 className="font-bold mb-2">Local Storage</h2>
          <pre className="bg-gray-100 p-2 rounded text-sm overflow-auto">
            {typeof window !== 'undefined' 
              ? localStorage.getItem('supabase.auth.token') || 'No token found'
              : 'Server side'}
          </pre>
        </div>
      </div>
    </div>
  )
}
