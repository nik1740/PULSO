import httpx
import sys
import os

BASE_URL = "http://localhost:8000"

def test_health():
    print(f"Testing {BASE_URL}/health...")
    try:
        response = httpx.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed!")
            print(response.json())
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Could not connect to server: {e}")
        return False
    return True

def test_protected_endpoint(token=None):
    print(f"\nTesting protected endpoint {BASE_URL}/api/v1/user/profile...")
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = httpx.get(f"{BASE_URL}/api/v1/user/profile", headers=headers)
        if response.status_code == 200:
            print("✅ Protected endpoint access successful!")
            print(response.json())
        elif response.status_code in [401, 403]:
            if token:
                print(f"❌ Access denied with token (Status {response.status_code}). Token might be invalid.")
            else:
                print(f"✅ Correctly denied access without token (Status {response.status_code}). Security is working.")
        else:
            print(f"⚠️ Unexpected status code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print(f"Using {httpx.__name__} version {httpx.__version__}")
    if not test_health():
        sys.exit(1)
    
    # Test without token (expecting verification of security)
    test_protected_endpoint()

    print("\nTo test with a real user, you need a Supabase JWT.")
    print("You can get one from your client app or Supabase dashboard.")
    print("Then update this script/request with 'Authorization: Bearer <TOKEN>'")
