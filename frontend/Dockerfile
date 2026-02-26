# ── Stage 1: Dependencies ─────────────────────────────────────────────────────
FROM node:20-alpine AS deps
WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

# ── Stage 2: Builder ───────────────────────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# ── Build-time variables ───────────────────────────────────────────────────────
# NEXT_PUBLIC_* vars are inlined into the JS bundle at build time.
# Set these as Railway Build Variables in your service settings:
#   NEXT_PUBLIC_API_URL          → https://your-backend.up.railway.app
#   NEXT_PUBLIC_SUPABASE_URL     → https://xxx.supabase.co
#   NEXT_PUBLIC_SUPABASE_ANON_KEY → your-anon-key
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_SUPABASE_URL
ARG NEXT_PUBLIC_SUPABASE_ANON_KEY

ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_SUPABASE_URL=$NEXT_PUBLIC_SUPABASE_URL
ENV NEXT_PUBLIC_SUPABASE_ANON_KEY=$NEXT_PUBLIC_SUPABASE_ANON_KEY

# Ensure public/ exists even if the project has none
RUN mkdir -p /app/public

RUN npm run build

# ── Stage 3: Runner ────────────────────────────────────────────────────────────
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
# Railway injects PORT at runtime; do NOT hardcode it here.
# HOSTNAME must be 0.0.0.0 so Next.js listens on all interfaces inside the container.
ENV HOSTNAME=0.0.0.0

# ── Runtime environment variables ──────────────────────────────────────────────
# Middleware (Edge Runtime) can read process.env at runtime for NON-NEXT_PUBLIC
# vars. Expose the Supabase credentials under non-prefixed names too so the
# middleware fallback picks them up even when the build args were missing.
# Railway will inject these from Service Variables at container start.
ARG NEXT_PUBLIC_SUPABASE_URL
ARG NEXT_PUBLIC_SUPABASE_ANON_KEY
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_SUPABASE_URL=$NEXT_PUBLIC_SUPABASE_URL
ENV NEXT_PUBLIC_SUPABASE_ANON_KEY=$NEXT_PUBLIC_SUPABASE_ANON_KEY
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV SUPABASE_URL=$NEXT_PUBLIC_SUPABASE_URL
ENV SUPABASE_ANON_KEY=$NEXT_PUBLIC_SUPABASE_ANON_KEY

# Non-root user for security
RUN addgroup --system --gid 1001 nodejs \
 && adduser  --system --uid 1001 nextjs

# Copy only the production-optimised standalone output
COPY --from=builder /app/public                                    ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone    ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static        ./.next/static

USER nextjs

# Informational – Railway auto-detects the port via $PORT env var
EXPOSE 3000

CMD ["node", "server.js"]
