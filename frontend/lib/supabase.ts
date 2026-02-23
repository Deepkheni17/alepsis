/**
 * Supabase Client Configuration
 *
 * Uses createBrowserClient from @supabase/ssr for proper cookie handling
 * with Next.js middleware auth.
 */

import { createBrowserClient } from '@supabase/ssr'

// NOTE: These env vars must be set in your Vercel dashboard under
// Settings → Environment Variables. They are public (NEXT_PUBLIC_) so
// they are embedded into the client bundle at build time.
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL ?? ''
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? ''

// Use createBrowserClient for proper cookie handling with Next.js middleware
export const supabase = createBrowserClient(supabaseUrl, supabaseAnonKey)
