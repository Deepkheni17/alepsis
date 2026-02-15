# Disable Email Confirmation for Instant Sign-Up

If sign-up is working but users need to confirm their email before signing in, disable email confirmation in Supabase for faster development.

## Steps to Disable Email Confirmation

1. **Go to Supabase Dashboard**: https://app.supabase.com
2. Select your project
3. Navigate to: **Authentication → Providers → Email**
4. Find **"Confirm email"** setting
5. **Toggle it OFF** (disable it)
6. Click **"Save"**

## What This Does

- Users can sign up and sign in immediately without email confirmation
- No need to check email during development
- Faster testing and development workflow

## For Production

Re-enable email confirmation before going to production to ensure users have valid email addresses.

## Current Behavior

With email confirmation:
- User signs up
- Receives confirmation email
- Must click link in email
- Then can sign in

Without email confirmation:
- User signs up
- Can immediately sign in
- No email required

## Alternative: Check Supabase Users

To verify your account is created:
1. Go to: https://app.supabase.com
2. Select your project
3. Navigate to: **Authentication → Users**
4. You should see your email in the list

If you see your email there, your account exists and you should be able to sign in.
