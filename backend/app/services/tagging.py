"""Utilities for assigning and managing tags."""

from __future__ import annotations

from typing import Dict, Iterable, List, Union
import re
import logging

from ..models import Tag


# Example keyword mapping. Keys may be tag names or IDs and values are lists of
# keywords or regular expression patterns. This mapping can be overridden when
# calling :func:`assign_tags`.
DEFAULT_KEYWORDS: Dict[Union[int, str], Iterable[str]] = {
    "Groceries": ["grocery", "supermarket", "market"],
    "Fuel": ["fuel", "gas", "petrol", "shell"],
}


def _find_tag(tag_key: Union[int, str]) -> Tag | None:
    """Return a ``Tag`` instance given an ID or name."""

    if isinstance(tag_key, int):
        return Tag.query.get(tag_key)
    return Tag.query.filter_by(name=tag_key).first()


def assign_tags(transaction, keywords: Dict[Union[int, str], Iterable[str]] | None = None) -> List[Tag]:
    """Return a list of tags matching the transaction description.

    Parameters
    ----------
    transaction:
        ``Transaction`` instance containing the description.
    keywords:
        Mapping of tag identifiers (name or ID) to lists of keywords or regex
        patterns. If ``None`` the :data:`DEFAULT_KEYWORDS` mapping is used.
    """

    keywords = keywords or DEFAULT_KEYWORDS
    description = (transaction.description or "").lower()
    logging.debug('Assigning tags for description: %s', description)
    matched: List[Tag] = []

    for tag_key, patterns in keywords.items():
        for pattern in patterns:
            tag = None
            if isinstance(pattern, re.Pattern):
                if pattern.search(description):
                    tag = _find_tag(tag_key)
            else:
                if str(pattern).lower() in description:
                    tag = _find_tag(tag_key)

            if tag and tag not in matched:
                matched.append(tag)
                logging.debug('Matched tag %s', tag.name)
                break

    if not matched:
        logging.info('No tags matched for description: %s', description)
    return matched
