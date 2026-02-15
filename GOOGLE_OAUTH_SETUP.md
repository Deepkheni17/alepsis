# Google OAuth Setup Guide

Google sign-in is currently disabled in the app. Follow these steps to enable it.

## Step 1: Configure Google Cloud Console

### 1.1 Access Google Cloud Console
Go to: https://console.cloud.google.com/apis/credentials

### 1.2 Create OAuth 2.0 Client ID (if not exists)

1. Click **"+ CREATE CREDENTIALS"**
2. Select **"OAuth client ID"**
3. If prompted to configure consent screen:
   - Click **"CONFIGURE CONSENT SCREEN"**
   - Choose **"External"** (for testing)
   - Fill in required fields:
     - App name: `Invoice Processing System`
     - User support email: Your email
     - Developer contact: Your email
   - Click **"SAVE AND CONTINUE"**
   - Skip scopes (click **"SAVE AND CONTINUE"**)
   - Add test users (your email)
   - Click **"SAVE AND CONTINUE"**

4. Back to "Create OAuth client ID":
   - Application type: **"Web application"**
   - Name: `Supabase Invoice App`

### 1.3 Add Authorized Redirect URI

In the **"Authorized redirect URIs"** section, add:

```
https://xpypmlgmeruqvzrmhyiy.supabase.co/auth/v1/callback
```

⚠️ **CRITICAL**: 
- Must use `https://` (not `http://`)
- No trailing slash
- Copy/paste exactly as shown

Click **"CREATE"**

### 1.4 Copy Credentials

You'll see a popup with:
- **Client ID** (starts with something like: 123456789-abc...)
- **Client Secret** (random string)

Keep this window open or save these values.

## Step 2: Configure Supabase

### 2.1 Access Supabase Dashboard
Go to: https://app.supabase.com

### 2.2 Enable Google Provider

1. Navigate to: **Authentication → Providers**
2. Find **"Google"** in the list
3. Click on it
4. Toggle **"Enable Google provider"** to ON
5. Paste your credentials:
   - **Client ID** (from Step 1.4)
   - **Client Secret** (from Step 1.4)
6. Verify the **Redirect URL** shown matches what you added in Google Console
7. Click **"Save"**

## Step 3: Enable Google Sign-In Button in Code

Edit `frontend/app/login/page.tsx`:

Find this line (around line 195):
```tsx
{false && (
```

Change it to:
```tsx
{true && (
```

Or simply remove the `{false && (` and matching `)}` to uncomment the section.

## Step 4: Test

1. Restart the frontend server (if it's running)
2. Go to: http://localhost:3000/login
3. Click **"Sign in with Google"**
4. Complete the Google sign-in flow
5. You should be redirected to the dashboard

## Troubleshooting

### Still getting redirect_uri_mismatch?

1. Double-check the redirect URI in Google Cloud Console matches exactly:
   ```
   https://xpypmlgmeruqvzrmhyiy.supabase.co/auth/v1/callback
   ```

2. Wait 1-2 minutes for Google's changes to propagate

3. Try in an incognito window

### Getting consent screen warning?

If you see "This app isn't verified" during sign-in:
- This is normal for development
- Click **"Advanced"** → **"Go to Invoice Processing System (unsafe)"**
- Or add your email as a test user in Google Cloud Console

## Current Status

✅ **Email/Password Login**: Working perfectly
❌ **Google OAuth**: Disabled until you complete the above steps

Once configured, Google sign-in provides a seamless one-click authentication experience.
