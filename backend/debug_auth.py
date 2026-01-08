import os
import httpx
from dotenv import load_dotenv
from jose import jwt

# Explicitly use the values provided by the user to be sure
# Or load from .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

print(f"URL: {SUPABASE_URL}")
print(f"KEY: {SUPABASE_KEY[:10]}...")
print(f"SECRET: {SUPABASE_JWT_SECRET}")

def get_token_dn():
    # Direct request to get a real token
    url = f"{SUPABASE_URL.rstrip('/')}/auth/v1/token?grant_type=password"
    email = input("\nEnter test user email: ")
    password = input("Enter test user password: ")
    
    resp = httpx.post(
        url, 
        headers={"apikey": SUPABASE_KEY, "Content-Type": "application/json"},
        json={"email": email, "password": password}
    )
    
    if resp.status_code != 200:
        print(f"❌ Login failed: {resp.text}")
        return None
        
    return resp.json()["access_token"]

def test_validation(token):
    print("\n--- Testing Validation Logic ---")
    try:
        # Try verifying with the secret exactly as is
        print("Attempt 1: Verifying with raw secret string...")
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False}
        )
        print("✅ Success! The secret is correct as a string.")
        return
    except Exception as e:
        print(f"❌ Failed: {e}")

    try:
        # Try verifying with base64 decoded secret (common if secret ends in ==)
        import base64
        print("\nAttempt 2: Verifying with base64 decoded secret...")
        decoded_secret = base64.b64decode(SUPABASE_JWT_SECRET) # Standard decoding
        # note: jose might want bytes or string, let's try bytes first
        payload = jwt.decode(
            token,
            decoded_secret,
            algorithms=["HS256"],
            options={"verify_aud": False}
        )
        print("✅ Success! The secret needed to be Base64 decoded.")
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    token = get_token_dn()
    if token:
        print(f"\nToken obtained: {token[:20]}...")
        test_validation(token)
