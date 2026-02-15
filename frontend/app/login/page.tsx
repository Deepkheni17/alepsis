'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '../../lib/supabase'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isSignUp, setIsSignUp] = useState(false)
  const [debugInfo, setDebugInfo] = useState<string>('')
  const router = useRouter()

  // Removed useEffect redirect - middleware handles this

  const handleEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setDebugInfo('')
    setLoading(true)

    console.log('🔐 Starting sign in...')
    setDebugInfo('Starting sign in...')

    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      })

      console.log('📦 Sign in response:', { data, error })
      setDebugInfo(`Response received. Error: ${error ? error.message : 'None'}. Session: ${data.session ? 'Yes' : 'No'}`)

      if (error) {
        console.error('❌ Sign in error:', error)
        if (error.message.includes('Email not confirmed')) {
          throw new Error('Please check your email and confirm your account before signing in.')
        } else if (error.message.includes('Invalid login credentials')) {
          throw new Error('Invalid email or password. Please try again.')
        }
        throw error
      }

      if (data.session) {
        console.log('✅ Session created:', data.session.user.email)
        setDebugInfo(`Session created for ${data.session.user.email}. Redirecting...`)
        console.log('🔄 Redirecting to dashboard...')
        
        // Give browser time to set cookies
        await new Promise(resolve => setTimeout(resolve, 300))
        
        // Use router.push for proper Next.js navigation
        router.push('/dashboard')
      } else {
        console.warn('⚠️ No session in response')
        setError('Sign in succeeded but no session was created. Please try again.')
        setDebugInfo('No session created!')
        setLoading(false)
      }
    } catch (err: any) {
      console.error('💥 Caught error:', err)
      setError(err.message || 'Login failed')
      setDebugInfo(`Error: ${err.message}`)
      setLoading(false)
    }
  }

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          emailRedirectTo: `${window.location.origin}/dashboard`
        }
      })

      if (error) throw error

      if (data.session) {
        // User is auto-confirmed, redirect immediately
        await new Promise(resolve => setTimeout(resolve, 300))
        router.push('/dashboard')
      } else if (data.user && data.user.identities && data.user.identities.length === 0) {
        setError('Email already registered. Please sign in instead.')
        setLoading(false)
      } else {
        setError('Account created! Please check your email to confirm your account, then sign in.')
        setLoading(false)
      }
    } catch (err: any) {
      setError(err.message || 'Sign up failed')
      setLoading(false)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    if (isSignUp) {
      handleSignUp(e)
    } else {
      handleEmailLogin(e)
    }
  }

  const handleGoogleLogin = async () => {
    setError(null)
    setLoading(true)

    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/dashboard`
        }
      })

      if (error) throw error
    } catch (err: any) {
      setError(err.message || 'Google login failed')
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow-md">
        <div>
          <h2 className="text-center text-3xl font-bold text-gray-900">
            {isSignUp ? 'Create your account' : 'Sign in to Invoice System'}
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            {isSignUp ? 'Start processing invoices today' : 'Access your invoice dashboard'}
          </p>
        </div>

        {error && (
          <div className={`${error.includes('check your email') ? 'bg-blue-50 border-blue-200 text-blue-700' : 'bg-red-50 border-red-200 text-red-700'} border px-4 py-3 rounded`}>
            {error}
          </div>
        )}

        {debugInfo && (
          <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded text-sm font-mono">
            Debug: {debugInfo}
          </div>
        )}

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="you@example.com"
                suppressHydrationWarning
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                minLength={6}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="••••••••"
                suppressHydrationWarning
              />
              {isSignUp && (
                <p className="mt-1 text-xs text-gray-500">
                  Minimum 6 characters
                </p>
              )}
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              suppressHydrationWarning
            >
              {loading ? (isSignUp ? 'Creating account...' : 'Signing in...') : (isSignUp ? 'Create account' : 'Sign in')}
            </button>
          </div>

          <div className="text-center">
            <button
              type="button"
              onClick={() => {
                setIsSignUp(!isSignUp)
                setError(null)
              }}
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              suppressHydrationWarning
            >
              {isSignUp ? 'Already have an account? Sign in' : "Don't have an account? Sign up"}
            </button>
          </div>
        </form>

        {/* Google Sign-In temporarily disabled - requires OAuth configuration */}
        {/* To enable: Configure redirect URI in Google Cloud Console */}
        {/* https://console.cloud.google.com/apis/credentials */}
        {/* Add: https://xpypmlgmeruqvzrmhyiy.supabase.co/auth/v1/callback */}
        {false && (
          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">Or continue with</span>
              </div>
            </div>

            <div className="mt-6">
              <button
                onClick={handleGoogleLogin}
                disabled={loading}
                className="w-full flex items-center justify-center gap-3 py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg className="w-5 h-5" viewBox="0 0 24 24">
                  <path
                    fill="currentColor"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="currentColor"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="currentColor"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  />
                  <path
                    fill="currentColor"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  />
                </svg>
                {isSignUp ? 'Sign up with Google' : 'Sign in with Google'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
