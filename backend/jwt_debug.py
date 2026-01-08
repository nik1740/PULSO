"""
JWT Debug Script - Run this to diagnose authentication issues
"""
import os
import base64
from dotenv import load_dotenv
from jose import jwt, JWTError

# Load .env
load_dotenv()

print("=" * 60)
print("JWT AUTHENTICATION DIAGNOSTIC")
print("=" * 60)

# 1. Check if all required env vars exist
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
jwt_secret = os.getenv("SUPABASE_JWT_SECRET")

print("\n[1] Environment Variables Check:")
print(f"  SUPABASE_URL: {'✅ Set' if supabase_url else '❌ MISSING'}")
print(f"  SUPABASE_SERVICE_KEY: {'✅ Set' if supabase_key else '❌ MISSING'}")
print(f"  SUPABASE_JWT_SECRET: {'✅ Set' if jwt_secret else '❌ MISSING'}")

if not jwt_secret:
    print("\n❌ SUPABASE_JWT_SECRET is not set! Add it to .env")
    exit(1)

# 2. Check JWT secret format
print("\n[2] JWT Secret Format Check:")
print(f"  Length: {len(jwt_secret)} characters")
print(f"  Starts with: {jwt_secret[:10]}...")
print(f"  Ends with: ...{jwt_secret[-10:]}")
print(f"  Contains '=': {'Yes (Base64 padded)' if '=' in jwt_secret else 'No'}")
print(f"  Contains spaces: {'⚠️ YES - PROBLEM!' if ' ' in jwt_secret else '✅ No'}")
print(f"  Contains quotes: {'⚠️ YES - PROBLEM!' if '\"' in jwt_secret or \"'\" in jwt_secret else '✅ No'}")

# 3. Try to get a real token
print("\n[3] Token Validation Test:")
print("  Enter a token from your Flutter app to test.")
print("  (In Flutter debug console, add: print(session.accessToken);)")
print("")

test_token = input("Paste your Supabase access token (or press Enter to skip): ").strip()

if test_token:
    print("\n  Testing token validation...")
    
    # Try with raw secret
    try:
        payload = jwt.decode(
            test_token,
            jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False}
        )
        print("  ✅ SUCCESS with raw secret!")
        print(f"  User ID: {payload.get('sub')}")
        print(f"  Email: {payload.get('email')}")
        print(f"  Role: {payload.get('role')}")
        exit(0)
    except JWTError as e:
        print(f"  ❌ Failed with raw secret: {e}")
    
    # Try with base64 decoded secret
    try:
        decoded_secret = base64.b64decode(jwt_secret)
        payload = jwt.decode(
            test_token,
            decoded_secret,
            algorithms=["HS256"],
            options={"verify_aud": False}
        )
        print("  ✅ SUCCESS with Base64-decoded secret!")
        print(f"  User ID: {payload.get('sub')}")
        print("  --> The secret needs Base64 decoding. auth.py already handles this.")
        exit(0)
    except Exception as e:
        print(f"  ❌ Failed with Base64 decoded secret: {e}")
    
    print("\n  ❌ Token could not be verified with either method.")
    print("  Possible causes:")
    print("    - Wrong JWT secret in .env")
    print("    - Token is expired")
    print("    - Token is from a different Supabase project")
else:
    print("  Skipped token test.")

print("\n" + "=" * 60)
print("NEXT STEPS:")
print("=" * 60)
print("1. If any checks above failed, fix those issues first.")
print("2. To get a token from Flutter, add this to api_service.dart:")
print("   print('DEBUG TOKEN: ${session.accessToken}');")
print("3. Run the app, trigger an analysis, and copy the printed token.")
print("4. Run this script again and paste the token to test.")
