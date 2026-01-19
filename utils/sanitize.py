import bleach
import re
from typing import Optional

def sanitize_text(value: Optional[str]) -> str:
    if not value:
        return ""
    return bleach.clean(
        value,
        tags=[],          # Remove ALL HTML tags
        attributes={},    # Remove inbuilt methods, etc.
        strip=True        # Strip the tags
    ).strip()

def sanitize_api_query(value: Optional[str], max_length: int = 100) -> str:
    """
    Sanitize query parameters for external API calls using an allow-list approach.
    Only permits alphanumeric characters, spaces, hyphens, underscores, periods,
    and the @ symbol (for email searches).
    
    This provides stronger protection against injection attacks (NoSQL, etc.)
    compared to HTML-only sanitization.
    """
    if not value:
        return ""
    
    # Allow-list: alphanumeric, spaces, common safe characters for search queries
    # Pattern allows: letters, numbers, spaces, hyphens, underscores, periods, @ (for emails)
    sanitized = re.sub(r'[^a-zA-Z0-9\s\-_.@]', '', value)
    
    # Collapse multiple spaces and strip
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    # Enforce maximum length to prevent DoS
    return sanitized[:max_length]
