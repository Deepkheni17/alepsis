# 🔄 Migration Guide - Adding Authentication to Existing Installation

## For Users With Existing Invoice System

If you already have the invoice system running without authentication, follow these steps to add Supabase authentication.

---

## ⚠️ Important Notes

- Your existing invoices will remain in the database
- After migration, all invoices need a `user_id`
- You'll need to create a Supabase account
- Existing database structure will be updated

---

## Step-by-Step Migration

### 1. **Backup Your Database** (CRITICAL)

Before making any changes:

```powershell
# Create a backup
pg_dump $env:DATABASE_URL > backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql
```

Or from Supabase Dashboard → Database → Backups

---

### 2. **Install New Dependencies**

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

---

### 3. **Create Supabase Project**

1. Go to https://supabase.com/dashboard
2. Create new project
3. **Use the same PostgreSQL database** or migrate data later
4. Get credentials from Settings → API:
   - Project URL
   - Anon Key
   - JWT Secret

---

### 4. **Update Environment Variables**

**Add to `e:\alepsis\.env`:**
```env
# Add these new variables (keep existing DATABASE_URL)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_JWT_SECRET=your-jwt-secret
SUPABASE_ANON_KEY=your-anon-key

# Keep your existing DATABASE_URL
DATABASE_URL=postgresql://...
```

**Create `e:\alepsis\frontend\.env.local`:**
```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

---

### 5. **Run Database Migration**

This will:
- Create `users` table
- Add `user_id` column to `invoices` table (nullable initially)
- Create foreign key relationship

```powershell
cd e:\alepsis
alembic upgrade head
```

---

### 6. **Handle Existing Invoices** (Optional)

If you have existing invoices without `user_id`, you have options:

#### Option A: Delete Old Invoices (Clean Start)
```sql
DELETE FROM invoices WHERE user_id IS NULL;
```

#### Option B: Create a Migration User
```sql
-- Create a default user for old invoices
INSERT INTO users (id, email, created_at) 
VALUES ('00000000-0000-0000-0000-000000000000', 'migration@system.local', NOW());

-- Assign all old invoices to this user
UPDATE invoices SET user_id = '00000000-0000-0000-0000-000000000000' WHERE user_id IS NULL;
```

#### Option C: Make user_id Required (After assigning)
```sql
-- After assigning all invoices to users
ALTER TABLE invoices ALTER COLUMN user_id SET NOT NULL;
```

---

### 7. **Update Frontend Routes**

The new system uses different routes:

**Old:**
- `/` - Dashboard with all invoices

**New:**
- `/` - Landing page
- `/login` - Authentication
- `/dashboard` - User dashboard (replaces old home)
- `/upload` - Upload page (now protected)
- `/invoices/[id]` - Detail page (now protected)

**What this means:**
- Existing bookmarks to `/` will show landing page
- Users must log in first
- After login, they go to `/dashboard`

---

### 8. **Test Migration**

1. Start servers:
   ```powershell
   # Backend
   cd e:\alepsis
   .\backend.ps1
   
   # Frontend
   cd e:\alepsis\frontend
   npm run dev
   ```

2. Open http://localhost:3000
3. Click "Sign In"
4. Create your first user account
5. Upload a test invoice
6. Verify it appears in your dashboard

---

### 9. **Verify Multi-User Isolation**

1. Create second user account (different email)
2. Upload different invoice
3. Log in as first user → see only first user's invoices
4. Log in as second user → see only second user's invoices

**If both users see all invoices:** Authentication is not working correctly

---

## 🔍 Troubleshooting Migration Issues

### "Column user_id does not exist"
→ Migration didn't run. Run: `alembic upgrade head`

### "Invalid JWT token"
→ `SUPABASE_JWT_SECRET` doesn't match your Supabase project

### "All users see all invoices"
→ Check that routes use `current_user = Depends(get_current_user)`
→ Check query filters include `Invoice.user_id == current_user.id`

### "Cannot login"
→ Enable Email provider in Supabase Dashboard → Authentication → Providers

### "Old invoices have no user"
→ Follow "Handle Existing Invoices" section above

---

## 🔄 Rolling Back (If Needed)

If something goes wrong:

### 1. Restore Database Backup
```powershell
psql $env:DATABASE_URL < backup_20240215_123456.sql
```

### 2. Rollback Migration
```powershell
alembic downgrade -1
```

### 3. Remove New Code
```powershell
git checkout <previous-commit>
```

---

## ✅ Migration Complete Checklist

- [ ] Database backed up
- [ ] Dependencies installed
- [ ] Supabase project created
- [ ] Environment variables updated
- [ ] Migration ran successfully
- [ ] Existing invoices handled
- [ ] First user created and tested
- [ ] Multi-user isolation verified
- [ ] Old bookmarks updated

---

## 📚 Next Steps

- Configure Google OAuth (optional)
- Set up password reset emails
- Enable MFA (Multi-Factor Authentication)
- Review user management in Supabase Dashboard
- Update any CI/CD pipelines with new env vars

---

## 🆘 Need Help?

- Check `QUICK_SETUP.md` for setup instructions
- Read `SUPABASE_SETUP.md` for detailed configuration
- Review `IMPLEMENTATION_CHECKLIST.md` for feature overview
- Check Supabase logs: Dashboard → Logs → Auth

---

## 🎉 Migration Benefits

✅ Multi-user support - Multiple accountants can use the system
✅ Data isolation - Users only see their own invoices
✅ Secure authentication - Industry-standard JWT tokens
✅ OAuth support - Google login option
✅ Session management - Stay logged in across tabs
✅ Production-ready - Supabase handles scaling and security
