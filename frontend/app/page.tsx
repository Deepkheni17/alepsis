'use client'
export const dynamic = 'force-dynamic'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import dynamicImport from 'next/dynamic'
import { supabase } from '@/lib/supabase'

// Lazy-load the heavy hero section (framer-motion + all landing page sections)
// so the initial JS bundle is minimal and the page loads fast.
const HeroSection = dynamicImport(
  () => import('@/components/blocks/hero-section').then(m => ({ default: m.HeroSection })),
  { loading: () => <div className="min-h-screen" />, ssr: false }
)

export default function Home() {
  const router = useRouter()

  useEffect(() => {
    // If already logged in, redirect straight to dashboard
    const checkSession = async () => {
      const { data: { session } } = await supabase.auth.getSession()
      if (session) {
        router.push('/dashboard')
      }
    }
    checkSession()
  }, [router])

  return <HeroSection />
}
