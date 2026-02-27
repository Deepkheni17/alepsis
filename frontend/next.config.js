/** @type {import('next').NextConfig} */

// In production (Vercel), set NEXT_PUBLIC_API_URL to your deployed backend URL.
// e.g. https://your-backend.railway.app
// In local dev, it defaults to http://127.0.0.1:8000
const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'

const nextConfig = {
  // ─── Expose env vars to all runtimes (middleware / server / client) ────────
  // This ensures SUPABASE_URL / SUPABASE_ANON_KEY are available in the Edge
  // Runtime middleware even if the NEXT_PUBLIC_ prefixed versions weren't set.
  env: {
    SUPABASE_URL:
      process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL || '',
    SUPABASE_ANON_KEY:
      process.env.SUPABASE_ANON_KEY ||
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ||
      '',
  },

  // ─── API Proxy ────────────────────────────────────────────────────────────
  // API requests are handled by the catch-all route handler at
  // app/api/[...path]/route.ts which proxies to the backend server-side.
  // This works in all deployment modes (dev, standalone, Railway, Vercel).

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
