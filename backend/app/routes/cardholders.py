from flask import Blueprint, request, jsonify

from .. import db
from ..models import Cardholder

bp = Blueprint('cardholders', __name__, url_prefix='/cardholders')


@bp.route('', methods=['GET'])
def list_cardholders():
    cardholders = Cardholder.query.all()
    return jsonify([
        {'id': c.id, 'name': c.name, 'color': c.color}
        for c in cardholders
    ])


@bp.route('', methods=['POST'])
def create_cardholder():
    payload = request.get_json() or {}
    cardholder = Cardholder(name=payload['name'], color=payload.get('color'))
    db.session.add(cardholder)
    db.session.commit()
    return jsonify({'id': cardholder.id}), 201
