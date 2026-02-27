/**
 * Catch-all API proxy route handler
 *
 * Proxies all /api/* requests to the FastAPI backend server-side.
 * This works in ALL deployment modes (dev, standalone, Railway, Vercel)
 * and eliminates CORS issues since it's a server-to-server call.
 */

import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL =
  process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'

async function proxyRequest(req: NextRequest) {
  // Extract the path after /api/
  const url = new URL(req.url)
  const path = url.pathname.replace(/^\/api/, '')
  const search = url.search // preserves query params like ?format=csv&status=PENDING

  const targetUrl = `${BACKEND_URL}${path}${search}`

  // Forward headers (especially Authorization)
  const headers = new Headers()
  req.headers.forEach((value, key) => {
    // Skip host/connection headers that shouldn't be forwarded
    if (!['host', 'connection', 'transfer-encoding'].includes(key.toLowerCase())) {
      headers.set(key, value)
    }
  })

  try {
    const fetchOptions: RequestInit = {
      method: req.method,
      headers,
      // @ts-ignore - duplex is needed for streaming request bodies
      duplex: 'half',
    }

    // Forward body for non-GET/HEAD requests
    if (req.method !== 'GET' && req.method !== 'HEAD') {
      fetchOptions.body = req.body
    }

    const backendRes = await fetch(targetUrl, fetchOptions)

    // Forward the response back to the client
    const responseHeaders = new Headers()
    backendRes.headers.forEach((value, key) => {
      // Don't forward hop-by-hop headers
      if (!['transfer-encoding', 'connection'].includes(key.toLowerCase())) {
        responseHeaders.set(key, value)
      }
    })

    return new NextResponse(backendRes.body, {
      status: backendRes.status,
      statusText: backendRes.statusText,
      headers: responseHeaders,
    })
  } catch (error: any) {
    console.error(`[API Proxy] Failed to reach backend at ${targetUrl}:`, error.message)
    return NextResponse.json(
      {
        success: false,
        error_type: 'BACKEND_UNREACHABLE',
        message: 'Backend service is unavailable. Please try again later.',
      },
      { status: 502 }
    )
  }
}

// Handle all HTTP methods
export const GET = proxyRequest
export const POST = proxyRequest
export const PUT = proxyRequest
export const PATCH = proxyRequest
export const DELETE = proxyRequest
