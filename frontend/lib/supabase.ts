/**
 * Supabase Client Configuration
 *
 * Uses createBrowserClient from @supabase/ssr for proper cookie handling
 * with Next.js middleware auth.
 */

import { createBrowserClient } from '@supabase/ssr'

// NOTE: These env vars must be set as Build Variables on Railway so they
// are embedded into the client bundle at build time.
// Lazy singleton: the client is only created on first access (at runtime),
// never at module-import time, which prevents build-time crashes when env
// vars are not yet available during static prerendering.
let _supabase: ReturnType<typeof createBrowserClient> | null = null

export const supabase = new Proxy({} as ReturnType<typeof createBrowserClient>, {
  get(_target, prop) {
    if (!_supabase) {
      const url = process.env.NEXT_PUBLIC_SUPABASE_URL ?? ''
      const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? ''
      _supabase = createBrowserClient(url, key)
    }
    return (_supabase as never)[prop as never]
  },
})
