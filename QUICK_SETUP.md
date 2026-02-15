# Quick Setup Guide - Supabase Authentication

## 🚀 Quick Start (5 minutes)

### 1. Install Dependencies

**Backend:**
```powershell
cd e:\alepsis
pip install python-jose[cryptography] PyJWT
```

**Frontend:**
```powershell
cd e:\alepsis\frontend
npm install @supabase/supabase-js @supabase/ssr
```

### 2. Create Supabase Project

1. Go to https://supabase.com/dashboard
2. Create new project
3. Wait 2-3 minutes for setup

### 3. Get Credentials

From Supabase Dashboard → Project Settings → API:

- Copy **Project URL**
- Copy **Anon key** 
- Copy **JWT Secret** (from JWT Settings)

### 4. Configure Backend

Create `e:\alepsis\.env`:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_JWT_SECRET=your-jwt-secret
SUPABASE_ANON_KEY=your-anon-key
DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres
```

Get DATABASE_URL from: Supabase → Settings → Database → Connection String

### 5. Configure Frontend

Create `e:\alepsis\frontend\.env.local`:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

### 6. Run Database Migration

```powershell
cd e:\alepsis
alembic upgrade head
```

This creates:
- ✅ users table
- ✅ user_id column in invoices
- ✅ Foreign key relationship

### 7. Enable Email Auth in Supabase

Supabase Dashboard → Authentication → Providers → Email
- ✅ Enable Email provider (default)

### 8. (Optional) Enable Google OAuth

Supabase Dashboard → Authentication → Providers → Google

**Get Google OAuth credentials:**
1. https://console.cloud.google.com
2. Create OAuth 2.0 Client ID
3. Add redirect URI: `https://your-project.supabase.co/auth/v1/callback`
4. Copy Client ID & Secret to Supabase

### 9. Start Servers

**Backend:**
```powershell
cd e:\alepsis
.\backend.ps1
# or: uvicorn app.main:app --reload
```

**Frontend:**
```powershell
cd e:\alepsis\frontend
npm run dev
```

### 10. Test It!

1. Open http://localhost:3000
2. Click "Sign In"
3. Create account or sign in with Google
4. Upload an invoice
5. Only you can see your invoices!

---

## ✅ What's Working Now

✅ Email/Password authentication
✅ Google OAuth login
✅ JWT token verification
✅ Protected routes (dashboard, upload, invoices)
✅ Multi-user data isolation
✅ User-specific invoice lists
✅ Ownership verification (403 if accessing others' invoices)
✅ Auto-create user on first login
✅ Session persistence across page refreshes

---

## 🔒 Security Features

✅ JWT tokens verified on every backend request
✅ User ID extracted from JWT (cannot be spoofed)
✅ All database queries filtered by user_id
✅ Middleware protects frontend routes
✅ No hardcoded secrets
✅ Environment variable separation (client vs server)

---

## 📁 Files Modified/Created

### Frontend
- ✅ `lib/supabase.ts` - Supabase client
- ✅ `app/login/page.tsx` - Login page
- ✅ `app/dashboard/page.tsx` - Protected dashboard
- ✅ `middleware.ts` - Route protection
- ✅ `app/page.tsx` - Landing page with auth redirect
- ✅ `app/upload/page.tsx` - Added auth
- ✅ `app/invoices/[id]/page.tsx` - Added auth
- ✅ `lib/api.ts` - Added auth headers
- ✅ `.env.local.example` - Environment template

### Backend
- ✅ `app/auth.py` - JWT verification (already existed)
- ✅ `app/models/orm_models.py` - User model (already existed)
- ✅ `app/api/routes.py` - Already using auth dependency
- ✅ `.env.template` - Environment template

### Database
- ✅ `alembic/versions/001_add_user_authentication.py` - Migration (already existed)

### Documentation
- ✅ `SUPABASE_SETUP.md` - Detailed setup guide
- ✅ `QUICK_SETUP.md` - This file

---

## 🐛 Troubleshooting

**"Invalid JWT token"**
→ Check SUPABASE_JWT_SECRET matches your project

**"Missing authentication credentials"**
→ Make sure you're logged in (check /login)

**Frontend redirect loop**
→ Clear browser cookies and localStorage

**CORS errors**
→ Backend should allow localhost:3000 (check main.py)

**User not auto-created**
→ Check database connection and migration ran successfully

**Google OAuth not working**
→ Verify redirect URI exactly matches Supabase callback URL

---

## 📚 Additional Resources

- 📖 Full setup guide: `SUPABASE_SETUP.md`
- 🔐 Supabase Auth docs: https://supabase.com/docs/guides/auth
- 🎨 Frontend environment: `.env.local.example`
- ⚙️ Backend environment: `.env.template`

---

## 🎯 Next Steps

1. ✅ Set up your `.env` files
2. ✅ Run migration
3. ✅ Test authentication
4. ✨ Customize login UI
5. 🚀 Deploy to production

---

## 💡 Testing Multi-User Isolation

1. Create account A and upload invoice
2. Logout
3. Create account B and upload different invoice
4. Login as A → see only A's invoices
5. Login as B → see only B's invoices
6. Try accessing A's invoice ID directly as B → 403 Forbidden

**Perfect isolation! 🎉**
