# Supabase Authentication Setup Guide

## ✅ Changes Applied

### 1. Created Files
- `app/auth.py` - JWT verification and user management
- `alembic/versions/001_add_user_authentication.py` - Database migration

### 2. Modified Files
- `app/models/orm_models.py` - Added User model and user_id to Invoice
- `app/api/routes.py` - Protected all invoice endpoints
- `app/services/export.py` - Added user_id filtering
- `requirements.txt` - Added pyjwt[crypto]
- `.env.example` - Added Supabase configuration

### 3. Installed Packages
- `pyjwt[crypto]` - For JWT verification

---

## 🔧 Setup Instructions

### Step 1: Configure Environment Variables

Add these to your `.env` file:

```bash
# Supabase Configuration
SUPABASE_URL=https://xpypmlgmeruqvzrmhyiy.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_JWT_SECRET=your-jwt-secret-here
```

**Where to find these:**
1. Go to Supabase Dashboard: https://app.supabase.com
2. Select your project
3. Go to Settings > API
4. Copy:
   - Project URL → `SUPABASE_URL`
   - anon/public key → `SUPABASE_ANON_KEY`
   - JWT Secret → `SUPABASE_JWT_SECRET`

### Step 2: Run Database Migration

```bash
# Activate virtual environment
& E:\alepsis\.venv\Scripts\Activate.ps1

# Run migration
alembic upgrade head
```

### Step 3: Enable Google OAuth in Supabase (Optional)

1. Go to Supabase Dashboard > Authentication > Providers
2. Enable Google provider
3. Add OAuth credentials from Google Cloud Console
4. Set redirect URLs

---

## 🔐 API Usage

### Authentication Flow

All invoice endpoints now require authentication:

```javascript
// 1. Sign in user (frontend)
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'password123'
});

// 2. Get access token
const { data: { session } } = await supabase.auth.getSession();
const token = session?.access_token;

// 3. Make authenticated request
const response = await fetch('http://localhost:8000/upload-invoice', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});
```

### Protected Endpoints

All these endpoints now require `Authorization: Bearer <token>`:

- `POST /upload-invoice` - Upload invoice (user-specific)
- `GET /invoices` - List invoices (user's only)
- `GET /invoices/{id}` - Get invoice (user's only)
- `GET /invoices/export` - Export invoices (user's only)
- `POST /invoices/{id}/approve` - Approve invoice (user's only)
- `DELETE /invoices/{id}` - Delete invoice (user's only)

### Error Responses

**401 Unauthorized:**
```json
{
  "detail": "Missing authentication credentials"
}
```

**404 Not Found:**
```json
{
  "detail": {
    "success": false,
    "error_type": "NOT_FOUND",
    "message": "Invoice with id 123 not found"
  }
}
```

---

## 🧪 Testing

### Test with cURL:

```bash
# Get token from Supabase (use actual token)
TOKEN="your.jwt.token.here"

# Test protected endpoint
curl -X GET http://localhost:8000/invoices \
  -H "Authorization: Bearer $TOKEN"
```

### Test User Creation:

When a user logs in for the first time:
1. JWT token is verified
2. User is automatically created in local `users` table
3. User ID matches Supabase Auth user ID
4. User can now create/view their invoices

---

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Invoices Table (Updated)
```sql
ALTER TABLE invoices 
ADD COLUMN user_id UUID REFERENCES users(id) ON DELETE CASCADE;
```

---

## 🚀 Next Steps

1. ✅ Add Supabase credentials to `.env`
2. ✅ Run database migration
3. ✅ Test authentication flow
4. Configure Google OAuth (optional)
5. Update frontend to handle auth
6. Test multi-user access control

---

## 🔍 Security Features

- ✅ JWT token verification with Supabase secret
- ✅ User isolation (users only see their own invoices)
- ✅ Foreign key constraints with CASCADE delete
- ✅ No hardcoded credentials
- ✅ Proper HTTP status codes (401, 404)
- ✅ Token expiration handling
- ✅ Invalid token handling

---

## 🐛 Troubleshooting

### "SUPABASE_JWT_SECRET is required"
- Missing environment variable
- Add to `.env` file from Supabase Dashboard

### "Token has expired"
- User needs to refresh token
- Implement token refresh in frontend

### "Invoice not found" (but it exists)
- Invoice belongs to a different user
- Check user authentication

### Migration fails
- Check DATABASE_URL is correct
- Ensure PostgreSQL is running
- Check for existing data conflicts
