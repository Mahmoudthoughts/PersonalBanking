import csv
import io
from datetime import datetime
from typing import Tuple, List

from .. import db
from ..models import Transaction

REQUIRED_FIELDS = ["transaction_date", "description", "total_amount"]


def export_transactions() -> str:
    """Return all transactions as CSV text."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "transaction_date",
        "posting_date",
        "description",
        "original_amount",
        "vat",
        "total_amount",
        "currency",
        "is_credit",
        "cardholder_name",
        "card_number",
        "cardholder_id",
    ])

    for t in Transaction.query.all():
        writer.writerow([
            t.transaction_date.isoformat(),
            t.posting_date.isoformat() if t.posting_date else "",
            t.description,
            str(t.original_amount) if t.original_amount is not None else "",
            str(t.vat) if t.vat is not None else "",
            str(t.total_amount) if t.total_amount is not None else "",
            t.currency or "",
            str(t.is_credit),
            t.cardholder_name or "",
            t.card_number or "",
            t.cardholder_id or "",
        ])
    return output.getvalue()


def import_transactions(file) -> Tuple[int, List[str]]:
    """Import transactions from an uploaded CSV file.

    Returns a tuple of (count, errors). If errors is non-empty, no data is committed.
    """
    text = file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))
    errors: List[str] = []
    transactions = []

    for i, row in enumerate(reader, start=1):
        missing = [f for f in REQUIRED_FIELDS if not row.get(f)]
        if missing:
            errors.append(f"row {i}: missing fields {', '.join(missing)}")
            continue
        try:
            transaction_date = datetime.fromisoformat(row["transaction_date"]).date()
        except Exception:
            errors.append(f"row {i}: invalid transaction_date")
            continue
        posting_date = None
        if row.get("posting_date"):
            try:
                posting_date = datetime.fromisoformat(row["posting_date"]).date()
            except Exception:
                errors.append(f"row {i}: invalid posting_date")
                continue
        try:
            total_amount = float(row["total_amount"])
        except Exception:
            errors.append(f"row {i}: invalid total_amount")
            continue

        def parse_optional_float(key: str):
            try:
                return float(row[key]) if row.get(key) else None
            except Exception:
                errors.append(f"row {i}: invalid {key}")
                return None

        original_amount = parse_optional_float("original_amount")
        vat = parse_optional_float("vat")

        if any(err.startswith(f"row {i}:") for err in errors):
            continue

        transaction = Transaction(
            transaction_date=transaction_date,
            posting_date=posting_date,
            description=row["description"],
            original_amount=original_amount,
            vat=vat,
            total_amount=total_amount,
            currency=row.get("currency"),
            is_credit=row.get("is_credit") == "True",
            cardholder_name=row.get("cardholder_name"),
            card_number=row.get("card_number"),
            cardholder_id=int(row["cardholder_id"]) if row.get("cardholder_id") else None,
        )
        transactions.append(transaction)

    if errors:
        return 0, errors

    for t in transactions:
        db.session.add(t)
    db.session.commit()
    return len(transactions), []
