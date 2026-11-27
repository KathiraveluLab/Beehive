import html
import bleach
import re
from typing import Optional

def sanitize_text(value: Optional[str]) -> str:
    """Strip HTML tags and return plain text.

    bleach.clean() escapes "&", "<" and ">", so "Tom & Jerry" would be stored
    as "Tom &amp; Jerry" and shown literally by the frontend, which already
    escapes text when it renders. The escaped output is therefore unescaped
    again. Unescaping can rebuild a tag out of input such as "<<b>b>", so the
    clean/unescape step repeats until the text stops changing.
    """
    if not value:
        return ""
    text = value
    while True:
        cleaned = html.unescape(
            bleach.clean(
                text,
                tags=[],          # Remove ALL HTML tags
                attributes={},    # Remove inbuilt methods, etc.
                strip=True        # Strip the tags
            )
        ).strip()
        if cleaned == text:
            return cleaned
        text = cleaned

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
