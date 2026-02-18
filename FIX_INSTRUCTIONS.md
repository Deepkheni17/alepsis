# 🔧 Fix: Invoice Upload & Fetch Errors

## Root Cause Identified ✓

**The SUPABASE_JWT_SECRET in your `.env` file is incomplete or incorrect.**

Current value: `ThJwPsejVVqkl-SUiUcS8w_OgBC25qQ` (too short)

Expected: A 400-500 character JWT secret from Supabase

---

## How to Fix (5 minutes)

### Step 1: Get Your Complete JWT Secret

1. Go to **https://app.supabase.com**
2. Select your project: `xpypmlgmeruqvzrmhyiy`
3. Go to **Settings** → **API**
4. Scroll down to **JWT Settings**
5. Copy the **JWT Secret** (it should be very long, ~400 characters)

### Step 2: Update `.env` File

Open `e:\alepsis\.env` and replace the current JWT secret:

```env
# OLD (WRONG):
SUPABASE_JWT_SECRET=ThJwPsejVVqkl-SUiUcS8w_OgBC25qQ

# NEW (CORRECT):
SUPABASE_JWT_SECRET=your-very-long-jwt-secret-from-supabase-dashboard
```

### Step 3: Restart Backend Server

```powershell
# Stop the current backend (Ctrl+C in the terminal)
# Then restart:
cd e:\alepsis
.\backend.ps1
```

### Step 4: Test

1. **Refresh your browser** (Ctrl+Shift+R)
2. Try uploading an invoice
3. Try viewing the invoices list

---

## Why This Was Failing

1. **Frontend** → Makes request with Supabase JWT token
2. **Backend** → Tries to verify token with `SUPABASE_JWT_SECRET`
3. **Verification fails** → Returns 401 Unauthorized
4. **UI shows** → "Failed to fetch invoices"

The JWT secret is like a password that must match exactly between Supabase and your backend.

---

## Verification

After fixing, you should see:

- ✅ Invoices page loads without error
- ✅ Upload invoice works successfully
- ✅ Dashboard shows invoice list

## Still Having Issues?

Check backend logs for authentication errors:
```powershell
# Look for lines like:
# "Token verification failed"
# "Invalid token"
```

---

**Note:** I've already fixed the API URL configuration in the frontend (`api.ts`), so once you update the JWT secret and restart the backend, everything should work!
