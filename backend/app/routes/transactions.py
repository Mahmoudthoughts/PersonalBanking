"""Transaction-related API routes using FastAPI."""

from __future__ import annotations

import logging
from datetime import date, datetime
import tempfile
from typing import List, Optional

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import joinedload

from .. import db
from ..models import Transaction, Tag
from ..services.pdf_parser import parse_pdf
from ..services.cardholder_mapping import guess_cardholder
from ..services.tagging import assign_tags, DEFAULT_KEYWORDS
from ..services.tag_ai import tag_ai


router = APIRouter()


@router.get("")
def list_transactions(
    amount: Optional[float] = None,
    tag: Optional[int] = None,
    cardholder: Optional[int] = None,
    desc: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    Authorize: AuthJWT = Depends(),
):
    """Return a filtered list of transactions."""
    Authorize.jwt_required()
    logger = logging.getLogger(__name__)
    logger.debug(
        "Listing transactions with args amount=%s tag=%s cardholder=%s desc=%s start=%s end=%s",
        amount,
        tag,
        cardholder,
        desc,
        start,
        end,
    )
    query = Transaction.query.options(joinedload(Transaction.tags))

    if amount is not None:
        query = query.filter(Transaction.total_amount == amount)
    if cardholder:
        query = query.filter(Transaction.cardholder_id == cardholder)
    if desc:
        query = query.filter(Transaction.description.ilike(f"%{desc}%"))
    if start:
        query = query.filter(Transaction.transaction_date >= date.fromisoformat(start))
    if end:
        query = query.filter(Transaction.transaction_date <= date.fromisoformat(end))
    if tag:
        query = query.join(Transaction.tags).filter(Tag.id == tag)

    transactions = query.all()
    logger.debug("Fetched %d transactions", len(transactions))
    data = [
        {
            "id": t.id,
            "transaction_date": t.transaction_date.isoformat(),
            "posting_date": t.posting_date.isoformat() if t.posting_date else None,
            "description": t.description,
            "original_amount": float(t.original_amount) if t.original_amount is not None else None,
            "vat": float(t.vat) if t.vat is not None else None,
            "total_amount": float(t.total_amount) if t.total_amount is not None else None,
            "card_number": t.card_number,
            "currency": t.currency,
            "is_credit": t.is_credit,
            "cardholder_id": t.cardholder_id,
            "cardholder_name": t.cardholder_name,
            "card_number": t.card_number,
            "tags": [
                {"id": tag.id, "name": tag.name, "parent_id": tag.parent_id}
                for tag in t.tags
            ],
        }
        for t in transactions
    ]
    logger.info("Returning %d transactions", len(data))
    return data


@router.get("/summary/daily")
def daily_summary(
    tag: Optional[int] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    Authorize: AuthJWT = Depends(),
):
    """Return total transaction amounts grouped by day."""
    Authorize.jwt_required()
    query = db.session.query(
        Transaction.transaction_date,
        db.func.sum(Transaction.total_amount).label("total"),
    )
    if tag:
        query = query.join(Transaction.tags).filter(Tag.id == tag)
    if start:
        query = query.filter(Transaction.transaction_date >= date.fromisoformat(start))
    if end:
        query = query.filter(Transaction.transaction_date <= date.fromisoformat(end))
    rows = (
        query.group_by(Transaction.transaction_date)
        .order_by(Transaction.transaction_date)
        .all()
    )
    return [
        {"date": r.transaction_date.isoformat(), "total": float(r.total or 0)}
        for r in rows
    ]


@router.post("/")
def create_transaction(payload: dict, Authorize: AuthJWT = Depends()):
    """Create a new transaction."""
    Authorize.jwt_required()
    logger = logging.getLogger(__name__)
    logger.debug("Creating transaction with payload %s", payload)
    transaction = Transaction(
        transaction_date=date.fromisoformat(payload["transaction_date"]),
        posting_date=date.fromisoformat(payload["posting_date"]) if payload.get("posting_date") else None,
        description=payload["description"],
        original_amount=payload.get("original_amount"),
        vat=payload.get("vat"),
        total_amount=payload.get("total_amount"),
        currency=payload.get("currency"),
        is_credit=payload.get("is_credit", False),
        card_number=payload.get("card_number"),
        cardholder_id=payload.get("cardholder_id"),
        cardholder_name=payload.get("cardholder_name"),
        source_file=payload.get("source_file"),
    )
    db.session.add(transaction)
    db.session.commit()
    logger.info("Created transaction id=%s", transaction.id)
    return {"id": transaction.id}


@router.post("/parse_pdf")
def parse_pdf_endpoint(
    file: UploadFile = File(...),
    Authorize: AuthJWT = Depends(),
):
    """Return parsed transactions from an uploaded PDF without saving."""
    Authorize.jwt_required()
    logger = logging.getLogger(__name__)
    logger.info("PDF parse request received: %s", file.filename)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name
    data = parse_pdf(tmp_path)
    logger.debug("Parsed %d transactions from PDF", len(data))
    return data


@router.post("/upload_pdf", status_code=201)
def upload_pdf(
    file: UploadFile = File(...),
    Authorize: AuthJWT = Depends(),
):
    """Upload a PDF statement and create transactions."""
    Authorize.jwt_required()
    logger = logging.getLogger(__name__)
    logger.info("PDF upload received: %s", file.filename)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name
    transactions = parse_pdf(tmp_path)
    logger.debug("Parsed %d transactions from PDF", len(transactions))
    created = 0
    for data in transactions:
        cardholder_id = guess_cardholder(data.get("description", ""), file.filename)
        transaction = Transaction(
            transaction_date=data["transaction_date"],
            posting_date=data.get("posting_date"),
            description=data["description"],
            original_amount=data.get("original_amount"),
            vat=data.get("vat"),
            total_amount=data.get("total_amount"),
            card_number=data.get("card_number"),
            cardholder_name=data.get("cardholder_name"),
            cardholder_id=cardholder_id,
            source_file=file.filename,
        )
        transaction.tags = assign_tags(transaction, DEFAULT_KEYWORDS)
        db.session.add(transaction)
        created += 1
    db.session.commit()
    logger.info("Created %d transactions from PDF %s", created, file.filename)
    return {"created": created}


@router.post("/batch", status_code=201)
def batch_create(payload: List[dict], Authorize: AuthJWT = Depends()):
    """Create multiple transactions from JSON payload."""
    Authorize.jwt_required()
    created = 0
    logger = logging.getLogger(__name__)
    for item in payload:
        try:
            transaction = Transaction(
                transaction_date=datetime.strptime(item["transaction_date"], "%d/%m/%Y").date(),
                posting_date=datetime.strptime(item["posting_date"], "%d/%m/%Y").date()
                if item.get("posting_date")
                else None,
                description=item["description"],
                original_amount=item.get("original_amount"),
                vat=item.get("vat"),
                total_amount=item.get("total_amount"),
                card_number=item.get("card_number"),
                cardholder_name=item.get("cardholder_name"),
                source_file=item.get("source_file"),
            )
        except Exception as exc:  # pragma: no cover - logging
            logger.error("Failed to parse item %s: %s", item, exc)
            continue
        db.session.add(transaction)
        created += 1
    db.session.commit()
    logger.info("Batch created %d transactions", created)
    return {"created": created}


@router.get("/{transaction_id}")
def get_transaction(transaction_id: int, Authorize: AuthJWT = Depends()):
    """Return a single transaction with components and tags."""
    Authorize.jwt_required()
    transaction = (
        Transaction.query.options(
            joinedload(Transaction.tags), joinedload(Transaction.components)
        ).get(transaction_id)
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="transaction not found")
    data = {
        "id": transaction.id,
        "transaction_date": transaction.transaction_date.isoformat(),
        "posting_date": transaction.posting_date.isoformat()
        if transaction.posting_date
        else None,
        "description": transaction.description,
        "original_amount": float(transaction.original_amount)
        if transaction.original_amount is not None
        else None,
        "vat": float(transaction.vat) if transaction.vat is not None else None,
        "total_amount": float(transaction.total_amount)
        if transaction.total_amount is not None
        else None,
        "card_number": transaction.card_number,
        "currency": transaction.currency,
        "is_credit": transaction.is_credit,
        "cardholder_id": transaction.cardholder_id,
        "cardholder_name": transaction.cardholder_name,
        "source_file": transaction.source_file,
        "components": [
            {
                "id": c.id,
                "label": c.label,
                "amount": float(c.amount) if c.amount is not None else None,
                "vat": float(c.vat) if c.vat is not None else None,
            }
            for c in transaction.components
        ],
        "tags": [{"id": t.id, "name": t.name} for t in transaction.tags],
    }
    return data


@router.patch("/{transaction_id}")
def update_transaction(
    transaction_id: int, payload: dict, Authorize: AuthJWT = Depends()
):
    """Update existing transaction fields."""
    Authorize.jwt_required()
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="transaction not found")
    if "cardholder_id" in payload:
        transaction.cardholder_id = payload["cardholder_id"]
    if "card_number" in payload:
        transaction.card_number = payload["card_number"]
    if "tags" in payload:
        tags = Tag.query.filter(Tag.id.in_(payload["tags"])).all()
        transaction.tags = tags
    db.session.commit()
    return {"id": transaction.id}


@router.get("/{transaction_id}/suggest-tags")
def suggest_tags_route(transaction_id: int, Authorize: AuthJWT = Depends()):
    """Return suggested tags for a transaction."""
    Authorize.jwt_required()
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="transaction not found")
    tags = assign_tags(transaction, DEFAULT_KEYWORDS)
    return [{"id": t.id, "name": t.name} for t in tags]


@router.get("/{transaction_id}/ai-tags")
def ai_tags_route(transaction_id: int, Authorize: AuthJWT = Depends()):
    """Return AI-ranked tag suggestions for a transaction."""
    Authorize.jwt_required()
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="transaction not found")
    suggestions = tag_ai.suggest(transaction.description)
    return suggestions

