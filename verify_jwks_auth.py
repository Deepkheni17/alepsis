"""
JWKS Authentication Diagnostic Tool

This script verifies that JWT authentication is working correctly
using JWKS (JSON Web Key Set) public key verification.

Usage:
    python verify_jwks_auth.py
    python verify_jwks_auth.py <jwt_token>
"""

import os
import sys
import requests
from dotenv import load_dotenv
from jwt import PyJWKClient
import jwt

# Load environment variables
load_dotenv()

def check_jwks_configuration():
    """Check if JWKS configuration is properly set up."""
    
    supabase_url = os.getenv("SUPABASE_URL")
    
    if not supabase_url:
        print("❌ ERROR: SUPABASE_URL not found in .env file")
        return False
    
    print(f"\n✅ Supabase URL: {supabase_url}")
    
    # Construct JWKS URL
    jwks_url = f"{supabase_url}/auth/v1/.well-known/jwks.json"
    print(f"✅ JWKS URL: {jwks_url}")
    
    # Test JWKS endpoint
    print(f"\n🔍 Testing JWKS endpoint...")
    try:
        response = requests.get(jwks_url, timeout=10)
        response.raise_for_status()
        jwks_data = response.json()
        
        if 'keys' in jwks_data and len(jwks_data['keys']) > 0:
            print(f"✅ JWKS endpoint is accessible")
            print(f"✅ Found {len(jwks_data['keys'])} public key(s)")
            
            # Show key details
            for i, key in enumerate(jwks_data['keys'], 1):
                print(f"\n   Key {i}:")
                print(f"   - Algorithm: {key.get('alg', 'N/A')}")
                print(f"   - Key Type: {key.get('kty', 'N/A')}")
                print(f"   - Key ID: {key.get('kid', 'N/A')}")
                print(f"   - Use: {key.get('use', 'N/A')}")
            
            return True
        else:
            print("❌ JWKS endpoint returned empty keys")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch JWKS: {str(e)}")
        return False


def test_jwks_client():
    """Test PyJWKClient initialization."""
    
    supabase_url = os.getenv("SUPABASE_URL")
    jwks_url = f"{supabase_url}/auth/v1/.well-known/jwks.json"
    
    print(f"\n🔧 Testing PyJWKClient initialization...")
    try:
        jwks_client = PyJWKClient(jwks_url, cache_keys=True, max_cached_keys=10)
        print("✅ PyJWKClient initialized successfully")
        return jwks_client
    except Exception as e:
        print(f"❌ Failed to initialize PyJWKClient: {str(e)}")
        return None


def verify_token(token: str, jwks_client: PyJWKClient):
    """Verify a JWT token using JWKS."""
    
    print(f"\n🔐 Verifying JWT token...")
    print(f"   Token preview: {token[:50]}...")
    
    try:
        # Get the signing key from JWKS
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        print(f"✅ Found signing key: {signing_key.key_id}")
        
        # Decode and verify token
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256", "ES256"],  # Support both RSA and Elliptic Curve
            audience="authenticated",
            options={
                "verify_aud": True,
                "verify_exp": True,
                "verify_signature": True
            }
        )
        
        print("\n✅ Token verified successfully!")
        print(f"\n📋 Token Payload:")
        print(f"   User ID: {payload.get('sub')}")
        print(f"   Email: {payload.get('email')}")
        print(f"   Role: {payload.get('role')}")
        print(f"   Audience: {payload.get('aud')}")
        print(f"   Issuer: {payload.get('iss')}")
        
        import time
        exp = payload.get('exp')
        if exp:
            expires_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(exp))
            print(f"   Expires: {expires_at}")
        
        return True
        
    except jwt.ExpiredSignatureError:
        print("❌ Token has expired")
        print("   → Get a fresh token by logging in again")
        return False
        
    except jwt.InvalidAudienceError:
        print("❌ Invalid token audience")
        return False
        
    except jwt.InvalidTokenError as e:
        print(f"❌ Token verification failed: {str(e)}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def print_usage():
    """Print usage instructions."""
    print("\n💡 HOW TO GET A TOKEN FOR TESTING:")
    print("   1. Open your app in a browser")
    print("   2. Open Developer Tools (F12)")
    print("   3. Go to Console tab")
    print("   4. Login to your app")
    print("   5. In console, run: supabase.auth.getSession()")
    print("   6. Copy the 'access_token' value")
    print("   7. Run: python verify_jwks_auth.py <paste-token-here>")


if __name__ == "__main__":
    print("=" * 70)
    print("JWKS AUTHENTICATION DIAGNOSTIC TOOL")
    print("=" * 70)
    
    # Step 1: Check JWKS configuration
    config_ok = check_jwks_configuration()
    
    if not config_ok:
        print("\n" + "=" * 70)
        print("\n🔧 ACTION REQUIRED:")
        print("   1. Check SUPABASE_URL in .env file")
        print("   2. Ensure your Supabase project is active")
        print("   3. Check internet connection")
        sys.exit(1)
    
    # Step 2: Test JWKS client
    jwks_client = test_jwks_client()
    
    if not jwks_client:
        print("\n" + "=" * 70)
        print("\n❌ JWKS client initialization failed")
        sys.exit(1)
    
    # Step 3: Test token verification if provided
    if len(sys.argv) > 1:
        test_token = sys.argv[1]
        token_ok = verify_token(test_token, jwks_client)
        
        if token_ok:
            print("\n" + "=" * 70)
            print("\n🎉 SUCCESS! Authentication is working correctly!")
            print("\n✅ Your backend will now:")
            print("   - Verify JWT tokens using JWKS public keys")
            print("   - No longer need SUPABASE_JWT_SECRET")
            print("   - Work with all Supabase authentication methods")
        else:
            print("\n" + "=" * 70)
            print("\n⚠️  Token verification failed")
            print("   Try getting a fresh token and test again")
    else:
        print_usage()
        print("\n" + "=" * 70)
        print("\n✅ JWKS Configuration is correct!")
        print("   Authentication should work once you restart the backend.")
        print("\n   To test with an actual token, run:")
        print("   python verify_jwks_auth.py <your-jwt-token>")
    
    print("\n" + "=" * 70)
