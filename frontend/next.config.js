/** @type {import('next').NextConfig} */

// In production (Vercel), set NEXT_PUBLIC_API_URL to your deployed backend URL.
// e.g. https://your-backend.railway.app
// In local dev, it defaults to http://127.0.0.1:8000
const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'

const nextConfig = {
  // ─── API Proxy ────────────────────────────────────────────────────────────
  // Proxies /api/* → backend, eliminating browser CORS issues.
  // On Vercel, set NEXT_PUBLIC_API_URL in the Vercel dashboard (Environment Variables).
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${BACKEND_URL}/:path*`,
      },
    ]
  },

  // ─── Build Safety ─────────────────────────────────────────────────────────
  // Don't fail the Vercel build on TypeScript errors (shown as warnings instead).
  // Remove this line once all type errors are resolved.
  typescript: {
    ignoreBuildErrors: false,
  },

  // Don't fail the build on ESLint errors (eslint not installed in Docker).
  eslint: {
    ignoreDuringBuilds: true,
  },

  // ─── Docker / Standalone Output ───────────────────────────────────────────
  // Produces a self-contained build in .next/standalone used by the Dockerfile.
  output: 'standalone',

  // ─── Performance ──────────────────────────────────────────────────────────
  // Enable React strict mode for better error detection in development.
  reactStrictMode: true,

  // Allow images from Supabase storage if you use next/image in future.
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '*.supabase.co',
      },
    ],
  },
}

module.exports = nextConfig
