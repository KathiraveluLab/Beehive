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
    Sanitize a search string used for admin lookups.
    Usernames may contain any character except '@' and emails may contain '+',
    so only control characters are removed here. Callers pass the result through
    re.escape before building a regex, so it can never act as an operator.
    """
    if not value:
        return ""

    sanitized = re.sub(r'[\x00-\x1f\x7f]', ' ', value)

    # Collapse multiple spaces and strip
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()

    # Enforce maximum length to prevent DoS
    return sanitized[:max_length]
