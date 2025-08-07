from datetime import date, datetime
from flask import Blueprint, request, jsonify, current_app, Response
from flask_jwt_extended import jwt_required

from .. import db
from ..models import Transaction, Tag
from sqlalchemy.orm import joinedload
import tempfile

from ..services.pdf_parser import parse_pdf
from ..services.cardholder_mapping import guess_cardholder
from ..services.tagging import assign_tags, DEFAULT_KEYWORDS
from ..services.import_export import export_transactions, import_transactions
from ..services.tag_ai import tag_ai

bp = Blueprint('transactions', __name__, url_prefix='/transactions')


@bp.route('', methods=['GET'])
@jwt_required()
def list_transactions():
    current_app.logger.debug('Listing transactions with args %s', request.args)
    query = Transaction.query.options(joinedload(Transaction.tags))

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
            'tags': [
                {
                    'id': tag.id,
                    'name': tag.name,
                    'parent_id': tag.parent_id,
                }
                for tag in t.tags
            ],
        }
        for t in transactions
    ]
    current_app.logger.info('Returning %d transactions', len(data))
    return jsonify(data)


@bp.route('/summary/daily', methods=['GET'])
@jwt_required()
def daily_summary():
    """Return total transaction amounts grouped by day."""
    tag_id = request.args.get('tag', type=int)
    start = request.args.get('start')
    end = request.args.get('end')

    query = db.session.query(
        Transaction.transaction_date,
        db.func.sum(Transaction.total_amount).label('total'),
    )

    if tag_id:
        query = query.join(Transaction.tags).filter(Tag.id == tag_id)
    if start:
        query = query.filter(Transaction.transaction_date >= date.fromisoformat(start))
    if end:
        query = query.filter(Transaction.transaction_date <= date.fromisoformat(end))

    rows = (
        query.group_by(Transaction.transaction_date)
        .order_by(Transaction.transaction_date)
        .all()
    )
    data = [
        {
            'date': r.transaction_date.isoformat(),
            'total': float(r.total or 0),
        }
        for r in rows
    ]
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
                transaction_date=datetime.strptime(item['transaction_date'], "%d/%m/%Y").date(),
                posting_date=datetime.strptime(item['posting_date'], "%d/%m/%Y").date() if item.get('posting_date') else None,
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


@bp.route('/export', methods=['GET'])
@jwt_required()
def export_csv():
    """Download all transactions as CSV."""
    csv_data = export_transactions()
    current_app.logger.info('Exporting transactions to CSV')
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=transactions.csv'},
    )


@bp.route('/import', methods=['POST'])
@jwt_required()
def import_csv():
    """Import transactions from a CSV upload."""
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'no file uploaded'}), 400
    count, errors = import_transactions(file)
    if errors:
        current_app.logger.warning('Import failed with errors: %s', errors)
        return jsonify({'errors': errors}), 400
    current_app.logger.info('Imported %d transactions from CSV', count)
    return jsonify({'imported': count}), 201


@bp.route('/<int:transaction_id>', methods=['GET'])
@jwt_required()
def get_transaction(transaction_id: int):
    """Return a single transaction with components and tags."""
    current_app.logger.debug('Fetching transaction %s', transaction_id)
    transaction = (
        Transaction.query.options(
            joinedload(Transaction.tags), joinedload(Transaction.components)
        ).get_or_404(transaction_id)
    )

    data = {
        'id': transaction.id,
        'transaction_date': transaction.transaction_date.isoformat(),
        'posting_date': transaction.posting_date.isoformat() if transaction.posting_date else None,
        'description': transaction.description,
        'original_amount': float(transaction.original_amount) if transaction.original_amount is not None else None,
        'vat': float(transaction.vat) if transaction.vat is not None else None,
        'total_amount': float(transaction.total_amount) if transaction.total_amount is not None else None,
        'card_number': transaction.card_number,
        'currency': transaction.currency,
        'is_credit': transaction.is_credit,
        'cardholder_id': transaction.cardholder_id,
        'cardholder_name': transaction.cardholder_name,
        'source_file': transaction.source_file,
        'components': [
            {
                'id': c.id,
                'label': c.label,
                'amount': float(c.amount) if c.amount is not None else None,
                'vat': float(c.vat) if c.vat is not None else None,
            }
            for c in transaction.components
        ],
        'tags': [{'id': t.id, 'name': t.name} for t in transaction.tags],
    }

    return jsonify(data)


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
    if 'tags' in payload:
        tags = Tag.query.filter(Tag.id.in_(payload['tags'])).all()
        transaction.tags = tags
    db.session.commit()
    current_app.logger.info('Updated transaction id=%s', transaction.id)
    return jsonify({'id': transaction.id})


@bp.route('/<int:transaction_id>/suggest-tags', methods=['GET'])
@jwt_required()
def suggest_tags(transaction_id: int):
    """Return suggested tags for a transaction."""
    current_app.logger.debug('Suggesting tags for transaction %s', transaction_id)
    transaction = Transaction.query.get_or_404(transaction_id)
    tags = assign_tags(transaction, DEFAULT_KEYWORDS)
    return jsonify([{'id': t.id, 'name': t.name} for t in tags])


@bp.route('/<int:transaction_id>/ai-tags', methods=['GET'])
@jwt_required()
def ai_tags(transaction_id: int):
    """Return AI-ranked tag suggestions for a transaction."""
    current_app.logger.debug('AI suggesting tags for transaction %s', transaction_id)
    transaction = Transaction.query.get_or_404(transaction_id)
    suggestions = tag_ai.suggest(transaction.description)
    return jsonify(suggestions)
