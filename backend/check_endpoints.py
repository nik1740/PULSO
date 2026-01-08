import httpx
import os
import sys
from dotenv import load_dotenv

BASE_URL = "http://localhost:8000"

def get_token():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
    
    if not url or not key:
        print("❌ Error: .env file missing Supabase credentials.")
        sys.exit(1)
        
    print("\n--- Login to Get Token ---")
    email = input("Email: ")
    password = input("Password: ")
    
    auth_url = f"{url}/auth/v1/token?grant_type=password"
    try:
        resp = httpx.post(auth_url, headers={"apikey": key}, json={"email": email, "password": password})
        if resp.status_code == 200:
            return resp.json()["access_token"]
        print(f"❌ Login failed: {resp.text}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Connection error: {e}")
        sys.exit(1)

def run_checks(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n--- Checking Protected Endpoints ---")
    
    endpoints = [
        ("GET", "/api/v1/user/profile"),
        ("GET", "/api/v1/user/medications"),
        ("GET", "/api/v1/ecg/sessions"),
        ("GET", "/api/v1/analysis/history/list"),
        # POSTs (Expect 422 Unprocessable Entity which confirms Auth passed)
        ("POST", "/api/v1/user/medications"), 
        ("POST", "/api/v1/ecg/questionnaire"),
        # ("POST", "/api/v1/ecg/snapshot/1"), # Needs file upload, complicated
        # ("POST", "/api/v1/analysis/request/1"), # Might trigger AI cost
    ]
    
    for method, path in endpoints:
        full_url = f"{BASE_URL}{path}"
        print(f"Checking {method} {path}...", end=" ")
        
        try:
            if method == "GET":
                resp = httpx.get(full_url, headers=headers)
                if resp.status_code == 200:
                    print("✅ OK (200)")
                else:
                    print(f"⚠️ Status {resp.status_code}")
            elif method == "POST":
                # Send empty body to trigger validation error (proving we passed auth)
                resp = httpx.post(full_url, headers=headers, json={})
                if resp.status_code == 422:
                    print("✅ Reachable (422 Validated)")
                elif resp.status_code == 401:
                    print("❌ Auth Failed (401)")
                else:
                    print(f"⚠️ Status {resp.status_code}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    token = get_token()
    run_checks(token)
