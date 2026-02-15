/* 
 * Quick Test: Check Supabase Email Confirmation Status
 * 
 * Run this in browser console on the login page to diagnose the issue
 */

async function checkEmailConfirmation() {
  const testEmail = 'deepkheni07@gmail.com';
  const testPassword = 'your-password-here'; // Replace with actual password

  console.log('🔍 Testing Supabase authentication...\n');

  try {
    // Import supabase from the global scope (assuming it's available)
    const { supabase } = await import('../../lib/supabase');

    console.log('1️⃣ Attempting to sign in...');
    const startTime = performance.now();

    const { data, error } = await supabase.auth.signInWithPassword({
      email: testEmail,
      password: testPassword,
    });

    const endTime = performance.now();
    const duration = (endTime - startTime).toFixed(0);

    if (error) {
      console.error(`❌ Sign in failed (${duration}ms):`, error.message);

      if (error.message.includes('Email not confirmed')) {
        console.log('\n📧 ISSUE FOUND: Email confirmation required!');
        console.log('\n✅ FIX:');
        console.log('1. Go to https://app.supabase.com');
        console.log('2. Select your project');
        console.log('3. Go to: Authentication → Providers → Email');
        console.log('4. Disable "Confirm email" toggle');
        console.log('5. Click Save');
        console.log('\nOR check your email for a confirmation link.');
      } else if (error.message.includes('Invalid')) {
        console.log('\n❌ ISSUE: Invalid credentials');
        console.log('Check your email/password are correct');
      }

      return;
    }

    if (data.session) {
      console.log(`✅ Sign in successful! (${duration}ms)`);
      console.log('Session:', {
        user: data.session.user.email,
        expires: new Date(data.session.expires_at * 1000).toLocaleString()
      });
      console.log('\n✨ Your authentication is working correctly!');
      console.log(`⏱️ Response time: ${duration}ms`);

      if (duration > 2000) {
        console.log('\n⚠️ Slow response detected. Possible causes:');
        console.log('- Slow network connection');
        console.log('- Supabase server delay');
        console.log('- Try: Restart browser or use incognito mode');
      }
    }

  } catch (err) {
    console.error('❌ Test failed:', err);
  }
}

// Usage: Copy this entire file content and paste in browser console
// Then run: checkEmailConfirmation()
