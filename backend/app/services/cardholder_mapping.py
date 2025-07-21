import re
from typing import Optional

# Map cardholder IDs to regex patterns that may appear in the
# transaction description or the uploaded filename. Adjust these
# patterns to match your actual statements.
CARDHOLDER_PATTERNS = {
    1: [re.compile(r"john", re.IGNORECASE)],
    2: [re.compile(r"mary", re.IGNORECASE)],
}


def guess_cardholder(description: str, filename: str) -> Optional[int]:
    """Attempt to determine the cardholder ID for a transaction."""
    text = f"{description} {filename}"
    for cid, patterns in CARDHOLDER_PATTERNS.items():
        for pattern in patterns:
            if pattern.search(text):
                return cid
    return None
