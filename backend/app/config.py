"""
PULSO Backend Configuration
Loads environment variables and provides settings singleton
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Supabase Configuration
    supabase_url: str
    supabase_service_key: str
    supabase_jwt_secret: str  # From Supabase Dashboard > Settings > API > JWT Secret
    
    # Gemini AI Configuration
    gemini_api_key: str
    
    # Application Settings
    environment: str = "development"
    
    # Rate Limiting (requests per minute per user)
    rate_limit_analysis: int = 5
    rate_limit_general: int = 60
    
    # JWT Configuration (Supabase uses HS256)
    jwt_algorithm: str = "HS256"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
