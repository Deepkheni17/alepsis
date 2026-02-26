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

function getSupabaseClient(): ReturnType<typeof createBrowserClient> {
  if (!_supabase) {
    const url = process.env.NEXT_PUBLIC_SUPABASE_URL ?? ''
    const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? ''

    if (!url || !key) {
      console.warn(
        '[supabase] NEXT_PUBLIC_SUPABASE_URL or NEXT_PUBLIC_SUPABASE_ANON_KEY is missing. ' +
          'Auth will not work until these are set as Railway build variables.'
      )
      // Return a lightweight no-op proxy so the app renders instead of
      // throwing an unrecoverable error. Any actual auth call will fail
      // gracefully at the network level.
      return new Proxy({} as ReturnType<typeof createBrowserClient>, {
        get(_t, prop) {
          if (prop === 'auth') {
            return new Proxy(
              {},
              {
                get() {
                  return async () => ({ data: { session: null, user: null }, error: new Error('Supabase not configured') })
                },
              }
            )
          }
          return () => {}
        },
      }) as ReturnType<typeof createBrowserClient>
    }

    _supabase = createBrowserClient(url, key)
  }
  return _supabase
}

export const supabase = new Proxy({} as ReturnType<typeof createBrowserClient>, {
  get(_target, prop) {
    return (getSupabaseClient() as never)[prop as never]
  },
})
