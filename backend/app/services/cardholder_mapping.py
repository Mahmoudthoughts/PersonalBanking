import re
import logging
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
    logging.debug('Guessing cardholder for text: %s', text)
    for cid, patterns in CARDHOLDER_PATTERNS.items():
        for pattern in patterns:
            if pattern.search(text):
                logging.debug('Matched cardholder %s', cid)
                return cid
    logging.warning('No cardholder match for transaction: %s', text)
    return None
