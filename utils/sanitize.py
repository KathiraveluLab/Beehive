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
