from datetime import date
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required

from .. import db
from ..models import Transaction, Tag
import tempfile

from ..services.pdf_parser import parse_pdf
from ..services.cardholder_mapping import guess_cardholder
from ..services.tagging import assign_tags, DEFAULT_KEYWORDS

bp = Blueprint('transactions', __name__, url_prefix='/transactions')


@bp.route('', methods=['GET'])
@jwt_required()
def list_transactions():
    current_app.logger.debug('Listing transactions with args %s', request.args)
    query = Transaction.query

    amount = request.args.get('amount', type=float)
    tag = request.args.get('tag', type=int)
    cardholder = request.args.get('cardholder', type=int)
    desc = request.args.get('desc')
    start = request.args.get('start')
    end = request.args.get('end')

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
    current_app.logger.debug('Fetched %d transactions', len(transactions))

    data = [
        {
            'id': t.id,
            'transaction_date': t.transaction_date.isoformat(),
            'posting_date': t.posting_date.isoformat() if t.posting_date else None,
            'description': t.description,
            'original_amount': float(t.original_amount) if t.original_amount is not None else None,
            'vat': float(t.vat) if t.vat is not None else None,
            'total_amount': float(t.total_amount) if t.total_amount is not None else None,
            'card_number': t.card_number,
            'currency': t.currency,
            'is_credit': t.is_credit,
            'cardholder_id': t.cardholder_id,
            'cardholder_name': t.cardholder_name,
            'card_number': t.card_number,
        }
        for t in transactions
    ]
    current_app.logger.info('Returning %d transactions', len(data))
    return jsonify(data)


@bp.route('', methods=['POST'])
@jwt_required()
def create_transaction():
    payload = request.get_json() or {}
    current_app.logger.debug('Creating transaction with payload %s', payload)
    transaction = Transaction(
        transaction_date=date.fromisoformat(payload['transaction_date']),
        posting_date=date.fromisoformat(payload['posting_date']) if payload.get('posting_date') else None,
        description=payload['description'],
        original_amount=payload.get('original_amount'),
        vat=payload.get('vat'),
        total_amount=payload.get('total_amount'),
        currency=payload.get('currency'),
        is_credit=payload.get('is_credit', False),
        card_number=payload.get('card_number'),
        cardholder_id=payload.get('cardholder_id'),
        cardholder_name=payload.get('cardholder_name'),
        source_file=payload.get('source_file'),
    )
    db.session.add(transaction)
    db.session.commit()
    current_app.logger.info('Created transaction id=%s', transaction.id)
    return jsonify({'id': transaction.id}), 201


@bp.route('/parse_pdf', methods=['POST'])
@jwt_required()
def parse_pdf_endpoint():
    """Return parsed transactions from an uploaded PDF without saving."""
    file = request.files.get('file')
    current_app.logger.info('PDF parse request received: %s', file.filename if file else None)
    if not file:
        return jsonify({'error': 'no file uploaded'}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    data = parse_pdf(tmp_path)
    current_app.logger.debug('Parsed %d transactions from PDF', len(data))
    return jsonify(data)


@bp.route('/upload_pdf', methods=['POST'])
@jwt_required()
def upload_pdf():
    """Upload a PDF statement and create transactions."""
    file = request.files.get('file')
    current_app.logger.info('PDF upload received: %s', file.filename if file else None)
    if not file:
        return jsonify({'error': 'no file uploaded'}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    transactions = parse_pdf(tmp_path)
    current_app.logger.debug('Parsed %d transactions from PDF', len(transactions))
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
            card_number=data.get('card_number'),
            cardholder_name=data.get('cardholder_name'),
            cardholder_id=cardholder_id,
            source_file=file.filename,
        )
        transaction.tags = assign_tags(transaction, DEFAULT_KEYWORDS)
        db.session.add(transaction)
        created += 1
    db.session.commit()
    current_app.logger.info('Created %d transactions from PDF %s', created, file.filename)
    return jsonify({'created': created}), 201


@bp.route('/batch', methods=['POST'])
@jwt_required()
def batch_create():
    """Create multiple transactions from JSON payload."""
    payload = request.get_json() or []
    if not isinstance(payload, list):
        return jsonify({'error': 'invalid payload'}), 400
    created = 0
    for item in payload:
        try:
            transaction = Transaction(
                transaction_date=date.fromisoformat(item['transaction_date']),
                posting_date=date.fromisoformat(item['posting_date']) if item.get('posting_date') else None,
                description=item['description'],
                original_amount=item.get('original_amount'),
                vat=item.get('vat'),
                total_amount=item.get('total_amount'),
                card_number=item.get('card_number'),
                cardholder_name=item.get('cardholder_name'),
                source_file=item.get('source_file'),
            )
        except Exception as exc:
            current_app.logger.error('Failed to parse item %s: %s', item, exc)
            continue
        db.session.add(transaction)
        created += 1
    db.session.commit()
    current_app.logger.info('Batch created %d transactions', created)
    return jsonify({'created': created}), 201


@bp.route('/<int:transaction_id>', methods=['PATCH'])
@jwt_required()
def update_transaction(transaction_id: int):
    """Update existing transaction fields."""
    current_app.logger.debug('Updating transaction %s', transaction_id)
    transaction = Transaction.query.get_or_404(transaction_id)
    payload = request.get_json() or {}
    if 'cardholder_id' in payload:
        transaction.cardholder_id = payload['cardholder_id']
    if 'card_number' in payload:
        transaction.card_number = payload['card_number']
    db.session.commit()
    current_app.logger.info('Updated transaction id=%s', transaction.id)
    return jsonify({'id': transaction.id})
