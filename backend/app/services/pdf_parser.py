"""Utilities for parsing uploaded PDF statements."""

from __future__ import annotations

from datetime import datetime
import re
from typing import List, Optional, Dict, Any

from pdfminer.high_level import extract_text


DATE_RE = re.compile(r"(\d{2}/\d{2}/\d{4})")
AMOUNT_RE = re.compile(r"[-+]?\d+(?:,\d{3})*(?:\.\d+)?")


def _parse_amount(value: str) -> float:
    """Convert a string amount to ``float``."""

    return float(value.replace(",", ""))


def _parse_start_line(line: str) -> Optional[Dict[str, Any]]:
    """Parse the first line of a transaction.

    Expected format (example)::

        Transaction Date 24/06/2025 Posting Date 25/06/2025 PlayStation ... 44.04 0.06 45.47

    Returns ``None`` if the line does not look like a transaction start.
    """

    if "transaction date" not in line.lower():
        return None

    m = re.search(
        r"Transaction Date\s*(?P<transaction_date>\d{2}/\d{2}/\d{4}).*?Posting Date\s*(?P<posting_date>\d{2}/\d{2}/\d{4})\s*(?P<body>.+)",
        line,
        re.IGNORECASE,
    )
    if not m:
        return None

    body = m.group("body")
    amounts = AMOUNT_RE.findall(body)
    if len(amounts) >= 3:
        original_amount = _parse_amount(amounts[-3])
        vat = _parse_amount(amounts[-2])
        total_amount = _parse_amount(amounts[-1])
        description_part = body.rsplit(amounts[-3], 1)[0].strip()
    else:
        # Fallback when amounts are not present as expected
        original_amount = vat = total_amount = None
        description_part = body.strip()

    return {
        "transaction_date": datetime.strptime(m.group("transaction_date"), "%d/%m/%Y").date(),
        "posting_date": datetime.strptime(m.group("posting_date"), "%d/%m/%Y").date(),
        "description": description_part,
        "original_amount": original_amount,
        "vat": vat,
        "total_amount": total_amount,
    }


def _parse_component_line(line: str) -> Optional[Dict[str, Any]]:
    """Parse a sub-line that might contain fee breakdown information."""

    numbers = AMOUNT_RE.findall(line)
    if not numbers:
        return None

    if len(numbers) >= 2:
        amount = _parse_amount(numbers[-2])
        vat = _parse_amount(numbers[-1])
        label = line.rsplit(numbers[-2], 1)[0].strip()
    else:
        amount = _parse_amount(numbers[-1])
        vat = None
        label = line.rsplit(numbers[-1], 1)[0].strip()

    return {"label": label, "amount": amount, "vat": vat}


def parse_pdf(file_path: str) -> List[Dict[str, Any]]:
    """Extract transactions from a PDF credit card statement.

    Parameters
    ----------
    file_path:
        Path to the PDF file.

    Returns
    -------
    List[Dict[str, Any]]
        A list of transaction dictionaries matching the expected schema.
    """

    text = extract_text(file_path)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    transactions: List[Dict[str, Any]] = []
    current: Optional[Dict[str, Any]] = None

    for line in lines:
        start = _parse_start_line(line)
        if start:
            if current:
                current["description"] = " ".join(current.pop("_desc_lines"))
                transactions.append(current)
            current = start
            current["components"] = []
            current["_desc_lines"] = [start.pop("description")]
            continue

        if not current:
            continue

        comp = _parse_component_line(line)
        if comp:
            current["components"].append(comp)
        current["_desc_lines"].append(line)

    if current:
        current["description"] = " ".join(current.pop("_desc_lines"))
        transactions.append(current)

    return transactions
