/** @type {import('next').NextConfig} */
const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'

const nextConfig = {
  // Proxy all /api/* requests to the backend server.
  // This eliminates CORS issues because the request goes
  // Next.js server → backend (same-origin from browser's perspective).
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${BACKEND_URL}/:path*`,
      },
    ]
  },
}

module.exports = nextConfig
