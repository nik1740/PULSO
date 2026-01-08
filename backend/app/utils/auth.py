"""
Authentication Utilities
JWT validation for Supabase tokens and user extraction
Updated to support both HS256 (legacy) and ES256 (new JWKS-based) tokens
"""
import base64
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError, jwk
from jose.utils import base64url_decode
from pydantic import BaseModel
from typing import Optional, Dict
from functools import lru_cache
from ..config import get_settings

# HTTP Bearer token scheme
security = HTTPBearer()


class TokenData(BaseModel):
    """Extracted data from JWT token"""
    user_id: str
    email: Optional[str] = None
    role: str = "authenticated"


class CurrentUser(BaseModel):
    """Current authenticated user"""
    id: str
    email: Optional[str] = None
    role: str = "authenticated"


@lru_cache(maxsize=1)
def get_jwks(supabase_url: str) -> Dict:
    """Fetch JWKS from Supabase (cached)"""
    jwks_url = f"{supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
    try:
        response = httpx.get(jwks_url, timeout=10.0)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Failed to fetch JWKS: {e}")
    return {"keys": []}


def get_signing_key(token: str, jwks: Dict) -> Optional[Dict]:
    """Get the signing key from JWKS that matches the token's kid"""
    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                return key
    except Exception as e:
        print(f"Error getting signing key: {e}")
    return None


def decode_supabase_token(token: str) -> dict:
    """
    Decode and validate Supabase JWT token
    
    Supports both:
    - ES256 (new JWKS-based signing)
    - HS256 (legacy secret-based signing)
    """
    settings = get_settings()
    
    # First, check what algorithm the token uses
    try:
        unverified_header = jwt.get_unverified_header(token)
        alg = unverified_header.get("alg", "HS256")
    except Exception:
        alg = "HS256"
    
    # Try ES256 with JWKS (new method)
    if alg == "ES256":
        try:
            jwks = get_jwks(settings.supabase_url)
            signing_key = get_signing_key(token, jwks)
            
            if signing_key:
                # Convert JWK to PEM format for jose
                from jose.backends import ECKey
                key = jwk.construct(signing_key)
                
                payload = jwt.decode(
                    token,
                    key,
                    algorithms=["ES256"],
                    options={"verify_aud": False}
                )
                return payload
        except Exception as e:
            print(f"ES256 verification failed: {e}")
            # Fall through to HS256 attempt
    
    # Try HS256 with legacy secret
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False}
        )
        return payload
    except JWTError:
        pass
    
    # Try HS256 with base64-decoded secret
    try:
        decoded_secret = base64.b64decode(settings.supabase_jwt_secret)
        payload = jwt.decode(
            token,
            decoded_secret,
            algorithms=["HS256"],
            options={"verify_aud": False}
        )
        return payload
    except Exception:
        pass
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication token: Could not verify signature",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CurrentUser:
    """
    FastAPI dependency to extract and validate current user from JWT
    """
    token = credentials.credentials
    payload = decode_supabase_token(token)
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user ID",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return CurrentUser(
        id=user_id,
        email=payload.get("email"),
        role=payload.get("role", "authenticated")
    )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[CurrentUser]:
    """
    Optional authentication - returns None if no token provided
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
