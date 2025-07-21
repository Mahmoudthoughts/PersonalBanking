from datetime import date
import os
from flask import Blueprint, request, jsonify

from .. import db
from ..models import Transaction, Tag
from ..services.pdf_parser import parse_pdf
from ..services.cardholder_mapping import guess_cardholder

bp = Blueprint('transactions', __name__, url_prefix='/transactions')


@bp.route('', methods=['GET'])
def list_transactions():
    query = Transaction.query

    amount = request.args.get('amount', type=float)
    tag = request.args.get('tag', type=int)
    cardholder = request.args.get('cardholder', type=int)
    desc = request.args.get('desc')
    start = request.args.get('start')
    end = request.args.get('end')

    if amount is not None:
        query = query.filter(Transaction.amount == amount)

    if cardholder:
        query = query.filter(Transaction.cardholder_id == cardholder)

    if desc:
        query = query.filter(Transaction.description.ilike(f"%{desc}%"))

    if start:
        query = query.filter(Transaction.date >= date.fromisoformat(start))

    if end:
        query = query.filter(Transaction.date <= date.fromisoformat(end))

    if tag:
        query = query.join(Transaction.tags).filter(Tag.id == tag)

    transactions = query.all()

    data = [
        {
            'id': t.id,
            'transaction_date': t.transaction_date.isoformat(),
            'posting_date': t.posting_date.isoformat() if t.posting_date else None,
            'description': t.description,
            'total_amount': float(t.total_amount) if t.total_amount is not None else None,
            'cardholder_id': t.cardholder_id,
        }
        for t in transactions
    ]
    return jsonify(data)


@bp.route('', methods=['POST'])
def create_transaction():
    payload = request.get_json() or {}
    transaction = Transaction(
        transaction_date=date.fromisoformat(payload['transaction_date']),
        posting_date=date.fromisoformat(payload['posting_date']) if payload.get('posting_date') else None,
        description=payload['description'],
        original_amount=payload.get('original_amount'),
        vat=payload.get('vat'),
        total_amount=payload.get('total_amount'),
        currency=payload.get('currency'),
        is_credit=payload.get('is_credit', False),
        cardholder_id=payload.get('cardholder_id'),
        source_file=payload.get('source_file'),
    )
    db.session.add(transaction)
    db.session.commit()
    return jsonify({'id': transaction.id}), 201


@bp.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    """Upload a PDF statement and create transactions."""
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'no file uploaded'}), 400

    tmp_path = os.path.join('.', file.filename)
    file.save(tmp_path)

    transactions = parse_pdf(tmp_path)
    created = 0
    for data in transactions:
        cardholder_id = guess_cardholder(data.get('description', ''), file.filename)
        transaction = Transaction(
            transaction_date=data['transaction_date'],
            posting_date=data.get('posting_date'),
            description=data['description'],
            original_amount=data.get('original_amount'),
            vat=data.get('vat'),
            total_amount=data.get('total_amount'),
            cardholder_id=cardholder_id,
            source_file=file.filename,
        )
        db.session.add(transaction)
        created += 1
    db.session.commit()

    return jsonify({'created': created}), 201


@bp.route('/<int:transaction_id>', methods=['PATCH'])
def update_transaction(transaction_id: int):
    """Update existing transaction fields."""
    transaction = Transaction.query.get_or_404(transaction_id)
    payload = request.get_json() or {}
    if 'cardholder_id' in payload:
        transaction.cardholder_id = payload['cardholder_id']
    db.session.commit()
    return jsonify({'id': transaction.id})
