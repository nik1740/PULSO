"""
Input Sanitization Utilities
Prevents XSS and injection attacks
"""
import bleach
import re
from typing import Optional


# Allowed HTML tags (none for strict sanitization)
ALLOWED_TAGS = []
ALLOWED_ATTRIBUTES = {}


def sanitize_string(value: Optional[str]) -> Optional[str]:
    """
    Sanitize a string input to prevent XSS and injection attacks
    
    - Removes HTML tags
    - Strips dangerous characters
    - Limits length
    """
    if value is None:
        return None
    
    # Remove HTML tags
    cleaned = bleach.clean(value, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
    
    # Remove null bytes and control characters
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', cleaned)
    
    # Strip leading/trailing whitespace
    cleaned = cleaned.strip()
    
    return cleaned


def sanitize_notes(value: Optional[str], max_length: int = 1000) -> Optional[str]:
    """
    Sanitize notes/text fields with length limit
    """
    if value is None:
        return None
    
    cleaned = sanitize_string(value)
    
    # Limit length
    if cleaned and len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    
    return cleaned


def is_valid_uuid(value: str) -> bool:
    """Check if a string is a valid UUID"""
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    return bool(uuid_pattern.match(value))
