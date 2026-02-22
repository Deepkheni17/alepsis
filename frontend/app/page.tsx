'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '../lib/supabase'
import { HeroSection } from '@/components/blocks/hero-section'

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
