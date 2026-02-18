"""
JWT Secret Diagnostic Tool

This script helps verify if your SUPABASE_JWT_SECRET is correct.
Run this to test JWT validation without starting the full backend.

Usage:
    python verify_jwt_secret.py
"""

import os
import sys
from dotenv import load_dotenv
import jwt

# Load environment variables
load_dotenv()

def check_jwt_secret():
    """Check if JWT secret is properly configured."""
    
    # Check if JWT secret exists
    jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
    
    if not jwt_secret:
        print("❌ ERROR: SUPABASE_JWT_SECRET not found in .env file")
        return False
    
    # Check JWT secret length
    print(f"\n📊 JWT Secret Analysis:")
    print(f"   Length: {len(jwt_secret)} characters")
    print(f"   Preview: {jwt_secret[:30]}..." if len(jwt_secret) > 30 else f"   Full: {jwt_secret}")
    
    if len(jwt_secret) < 200:
        print("\n⚠️  WARNING: JWT Secret seems too short!")
        print("   Expected: ~400-500 characters from Supabase")
        print("   Current: Only {} characters".format(len(jwt_secret)))
        print("\n   → This might be incomplete or incorrect")
        return False
    
    print("\n✅ JWT Secret length looks correct")
    
    # Test with a sample Supabase token structure
    print("\n🔍 To fully verify, you need a real token from your Supabase auth.")
    print("   Get one by logging in from the frontend and checking browser console.")
    
    return True


def test_token_verification(test_token: str = None):
    """Test token verification if a token is provided."""
    
    if not test_token:
        print("\n💡 TIP: To test with a real token:")
        print("   1. Open browser console (F12)")
        print("   2. Login to the app")
        print("   3. Run: supabase.auth.getSession()")
        print("   4. Copy the access_token")
        print("   5. Run: python verify_jwt_secret.py <token>")
        return
    
    jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
    
    print("\n🔐 Testing Token Verification...")
    
    try:
        payload = jwt.decode(
            test_token,
            jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
            options={
                "verify_aud": True,
                "verify_exp": True,
                "verify_signature": True
            }
        )
        
        print("✅ Token verified successfully!")
        print(f"\n📋 Token Payload:")
        print(f"   User ID: {payload.get('sub')}")
        print(f"   Email: {payload.get('email')}")
        print(f"   Role: {payload.get('role')}")
        
        return True
        
    except jwt.ExpiredSignatureError:
        print("❌ Token has expired")
        print("   → Get a fresh token by logging in again")
        return False
        
    except jwt.InvalidTokenError as e:
        print(f"❌ Token verification failed: {str(e)}")
        print("   → JWT Secret might be incorrect")
        print("   → Make sure SUPABASE_JWT_SECRET matches your Supabase project")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("JWT SECRET DIAGNOSTIC TOOL")
    print("=" * 60)
    
    # Check JWT secret configuration
    secret_ok = check_jwt_secret()
    
    # If token provided as argument, test it
    if len(sys.argv) > 1:
        test_token = sys.argv[1]
        test_token_verification(test_token)
    else:
        test_token_verification()
    
    print("\n" + "=" * 60)
    
    if not secret_ok:
        print("\n🔧 ACTION REQUIRED:")
        print("   1. Go to https://app.supabase.com")
        print("   2. Select your project")
        print("   3. Settings → API → JWT Settings")
        print("   4. Copy the JWT Secret (should be ~400 characters)")
        print("   5. Update SUPABASE_JWT_SECRET in .env file")
        print("   6. Restart backend server")
        print("\n   See FIX_INSTRUCTIONS.md for detailed steps")
    else:
        print("\n✅ Configuration looks good!")
        print("   If you're still having issues:")
        print("   1. Restart the backend server")
        print("   2. Clear browser cache (Ctrl+Shift+R)")
        print("   3. Try logging in again")
