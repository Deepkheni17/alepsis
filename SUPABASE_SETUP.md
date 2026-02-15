# Supabase Authentication Setup Guide

## Prerequisites

1. **Supabase Account**: Sign up at https://supabase.com
2. **Google OAuth Credentials** (for Google login)

---

## 1. Create Supabase Project

1. Go to https://app.supabase.com
2. Click "New Project"
3. Fill in project details
4. Wait for project initialization

---

## 2. Get Supabase Credentials

### From Project Settings → API

Copy these values:

- **Project URL** → `SUPABASE_URL`
- **Anon/Public Key** → `SUPABASE_ANON_KEY`

### Get JWT Secret

From Project Settings → API → JWT Settings:

- **JWT Secret** → `SUPABASE_JWT_SECRET`

---

## 3. Enable Authentication Providers

### Email/Password (Enabled by default)

Go to **Authentication → Providers → Email**

- Enable "Email provider"
- Configure confirmation settings (optional)

### Google OAuth

1. Go to **Authentication → Providers → Google**

2. Create Google OAuth Credentials:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create new project or select existing
   - Enable Google+ API
   - Go to Credentials → Create OAuth 2.0 Client ID
   - Application type: Web application
   - Add authorized redirect URIs:
     ```
     https://YOUR_PROJECT_REF.supabase.co/auth/v1/callback
     ```

3. Copy Client ID and Client Secret to Supabase

4. Enable Google provider in Supabase

---

## 4. Configure Backend Environment Variables

Create/update `e:\alepsis\.env`:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_JWT_SECRET=your-jwt-secret-here
SUPABASE_ANON_KEY=your-anon-key-here

# Database Configuration
DATABASE_URL=postgresql://postgres:your-password@db.your-project-ref.supabase.co:5432/postgres
```

### Getting Database URL

From Supabase Project Settings → Database → Connection String:
- Copy the PostgreSQL connection string (in transaction pooling mode)
- Replace `[YOUR-PASSWORD]` with your database password

---

## 5. Configure Frontend Environment Variables

Create `e:\alepsis\frontend\.env.local`:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project-ref.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
```

**Important**: Only use `NEXT_PUBLIC_` prefix for variables that should be exposed to the browser.

---

## 6. Database Setup

The User and Invoice tables with proper relationships are already defined in the backend.

Run migrations to create tables:

```powershell
cd e:\alepsis
alembic upgrade head
```

This will create:
- `users` table (synced with Supabase Auth)
- `invoices` table (with `user_id` foreign key)

---

## 7. Test Authentication

### Start Backend

```powershell
cd e:\alepsis
.\backend.ps1
```

Backend runs on: http://localhost:8000

### Start Frontend

```powershell
cd e:\alepsis
.\frontend.ps1
```

Frontend runs on: http://localhost:3000

### Test Flow

1. Go to http://localhost:3000
2. Click "Sign In"
3. Try:
   - Email/password signup (if enabled)
   - Google OAuth login
4. After login, you should be redirected to `/dashboard`
5. Upload an invoice - it should be associated with your user

---

## 8. Security Checklist

✅ **Never commit** `.env` or `.env.local` files
✅ Keep `JWT_SECRET` private (server-side only)
✅ Use `ANON_KEY` for client-side (has limited permissions)
✅ All backend routes protected with `get_current_user` dependency
✅ Database queries filtered by `user_id`

---

## 9. Troubleshooting

### "Invalid JWT"

- Check `SUPABASE_JWT_SECRET` matches Supabase project
- Verify token is being sent in `Authorization: Bearer <token>` header

### "User not found"

- User is auto-created on first authenticated request
- Check database connection in backend

### Google OAuth Redirect Error

- Verify redirect URI in Google Console matches Supabase callback URL
- Check Google OAuth is enabled in Supabase

### CORS Errors

- Backend allows all origins (configured in FastAPI)
- For production, restrict CORS to your domain

---

## 10. Production Deployment

### Backend

1. Set environment variables in hosting platform
2. Use production PostgreSQL URL
3. Enable HTTPS
4. Restrict CORS to frontend domain

### Frontend

1. Set `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`
2. Update Google OAuth redirect URI to production domain
3. Deploy to Vercel/Netlify/etc.

### Database

- Use Supabase production database
- Enable Row Level Security (RLS) for additional protection
- Set up database backups

---

## Authentication Flow

```
1. User visits /login
2. Signs in with email/password or Google
3. Supabase returns JWT access_token
4. Frontend stores token in cookies (auto-managed by Supabase client)
5. Frontend sends token in Authorization header to backend
6. Backend verifies token using JWT_SECRET
7. Backend extracts user_id from token
8. Backend creates/gets User record in local database
9. All invoice operations filtered by user_id
```

---

## Multi-User Isolation

Each user can only:
- ✅ Upload their own invoices
- ✅ View their own invoices
- ✅ Approve/delete their own invoices
- ✅ Export only their own invoices

Users **cannot** access other users' data - enforced at:
1. Database query level (filtered by `user_id`)
2. Route dependency level (`current_user` from JWT)
3. Ownership verification (403 Forbidden if mismatch)

---

## Next Steps

- Configure email templates in Supabase
- Set up password reset flow
- Add user profile management
- Enable MFA (Multi-Factor Authentication)
- Implement Row Level Security in database
