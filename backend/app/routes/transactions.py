from datetime import date
from flask import Blueprint, request, jsonify

from .. import db
from ..models import Transaction

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
    )
    db.session.add(transaction)
    db.session.commit()
    return jsonify({'id': transaction.id}), 201
