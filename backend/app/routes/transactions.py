from datetime import date
import os
from flask import Blueprint, request, jsonify

from .. import db
from ..models import Transaction
from ..services.pdf_parser import parse_pdf

bp = Blueprint('transactions', __name__, url_prefix='/transactions')


@bp.route('', methods=['GET'])
def list_transactions():
    transactions = Transaction.query.all()
    data = [
        {
            'id': t.id,
            'date': t.date.isoformat(),
            'description': t.description,
            'amount': float(t.amount),
            'cardholder_id': t.cardholder_id,
        }
        for t in transactions
    ]
    return jsonify(data)


@bp.route('', methods=['POST'])
def create_transaction():
    payload = request.get_json() or {}
    transaction = Transaction(
        date=date.fromisoformat(payload['date']),
        description=payload['description'],
        amount=payload['amount'],
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

    tmp_path = os.path.join('/tmp', file.filename)
    file.save(tmp_path)

    transactions = parse_pdf(tmp_path)
    created = 0
    for data in transactions:
        transaction = Transaction(
            date=data['transaction_date'],
            description=data['description'],
            amount=data['total_amount'],
            cardholder_id=data.get('cardholder_id'),
            source_file=file.filename,
        )
        db.session.add(transaction)
        created += 1
    db.session.commit()

    return jsonify({'created': created}), 201
