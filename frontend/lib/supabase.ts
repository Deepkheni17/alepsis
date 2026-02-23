/**
 * Supabase Client Configuration
 * 
 * Provides authenticated Supabase client for browser with proper cookie handling.
 */

import { createBrowserClient } from '@supabase/ssr'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables. Check NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY')
}

// Use createBrowserClient for proper cookie handling with Next.js middleware
export const supabase = createBrowserClient(supabaseUrl, supabaseAnonKey)
