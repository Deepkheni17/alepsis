import { createServerClient, type CookieOptions } from '@supabase/ssr'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

/**
 * Helper: check whether a path requires authentication.
 */
const PROTECTED_PATHS = ['/dashboard', '/upload', '/invoices']
function isProtected(pathname: string): boolean {
  return PROTECTED_PATHS.some((p) => pathname.startsWith(p))
}

export async function middleware(req: NextRequest) {
  let response = NextResponse.next({
    request: { headers: req.headers },
  })

  // ── Resolve Supabase credentials ──────────────────────────────
  // NEXT_PUBLIC_* vars are inlined at build time. Fall back to
  // non-prefixed runtime env vars so the middleware also works when
  // the Railway runtime vars are set but the build args were not.
  const supabaseUrl =
    process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL || ''
  const supabaseKey =
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || process.env.SUPABASE_ANON_KEY || ''

  // If credentials are missing, gracefully degrade:
  //   • protected routes → redirect to /login
  //   • everything else  → pass through without auth check
  if (!supabaseUrl || !supabaseKey) {
    if (isProtected(req.nextUrl.pathname)) {
      const url = req.nextUrl.clone()
      url.pathname = '/login'
      return NextResponse.redirect(url)
    }
    return response
  }

  // ── Create Supabase server client ─────────────────────────────
  // Wrapped in try/catch so a misconfigured project URL / key
  // never crashes the whole middleware with a 500.
  let session: any = null
  try {
    const supabase = createServerClient(supabaseUrl, supabaseKey, {
      cookies: {
        get(name: string) {
          return req.cookies.get(name)?.value
        },
        set(name: string, value: string, options: CookieOptions) {
          req.cookies.set({ name, value, ...options })
          response = NextResponse.next({ request: { headers: req.headers } })
          response.cookies.set({ name, value, ...options })
        },
        remove(name: string, options: CookieOptions) {
          req.cookies.set({ name, value: '', ...options })
          response = NextResponse.next({ request: { headers: req.headers } })
          response.cookies.set({ name, value: '', ...options })
        },
      },
    })

    const { data } = await supabase.auth.getSession()
    session = data?.session ?? null
  } catch (err) {
    // Supabase client creation or getSession failed – treat as
    // unauthenticated rather than killing the request with a 500.
    console.error('[middleware] Supabase auth error:', err)
    session = null
  }

  // ── Route guards ──────────────────────────────────────────────
  if (isProtected(req.nextUrl.pathname) && !session) {
    const url = req.nextUrl.clone()
    url.pathname = '/login'
    return NextResponse.redirect(url)
  }

  if (req.nextUrl.pathname === '/login' && session) {
    const url = req.nextUrl.clone()
    url.pathname = '/dashboard'
    return NextResponse.redirect(url)
  }

  return response
}

export const config = {
  matcher: ['/dashboard/:path*', '/upload/:path*', '/invoices/:path*', '/login'],
}
