import os
import httpx
from dotenv import load_dotenv

def get_supabase_token():
    load_dotenv()
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
    
    if not url or not key:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY (or SUPABASE_SERVICE_KEY) must be set in .env")
        return

    # Construct the Auth URL correctly
    # Ensure URL doesn't end with slash when appending
    base_url = url.rstrip('/')
    auth_url = f"{base_url}/auth/v1/token?grant_type=password"

    print("\n--- Generate Supabase JWT (Direct API) ---")
    email = input("Enter test user email: ")
    password = input("Enter test user password: ")

    headers = {
        "apikey": key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "email": email,
        "password": password
    }

    try:
        print(f"\nConnecting to {base_url}...")
        response = httpx.post(auth_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token")
            
            print("\n✅ Authentication Successful!")
            print("\nCopy this Access Token into Swagger UI 'Value' field:")
            print("-" * 20)
            print(access_token)
            print("-" * 20)
        else:
            print(f"\n❌ Login Failed (Status {response.status_code})")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ Connection Error: {e}")

if __name__ == "__main__":
    get_supabase_token()
