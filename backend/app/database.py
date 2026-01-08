"""
Supabase Database Client
Provides database connection for the application
"""
from supabase import create_client, Client
from .config import get_settings

_supabase_client: Client = None


def get_supabase() -> Client:
    """Get Supabase client singleton"""
    global _supabase_client
    
    if _supabase_client is None:
        settings = get_settings()
        _supabase_client = create_client(
            settings.supabase_url,
            settings.supabase_service_key
        )
    
    return _supabase_client


def get_storage_client():
    """Get Supabase storage client for file uploads"""
    return get_supabase().storage
