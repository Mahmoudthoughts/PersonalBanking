from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required

from .. import db
from ..models import Cardholder

bp = Blueprint('cardholders', __name__, url_prefix='/cardholders')


@bp.route('', methods=['GET'])
@jwt_required()
def list_cardholders():
    current_app.logger.debug('Listing cardholders')
    cardholders = Cardholder.query.all()
    return jsonify([
        {'id': c.id, 'name': c.name, 'color': c.color}
        for c in cardholders
    ])


@bp.route('', methods=['POST'])
@jwt_required()
def create_cardholder():
    payload = request.get_json() or {}
    current_app.logger.info('Creating cardholder %s', payload.get('name'))
    cardholder = Cardholder(name=payload['name'], color=payload.get('color'))
    db.session.add(cardholder)
    db.session.commit()
    current_app.logger.debug('Created cardholder id=%s', cardholder.id)
    return jsonify({'id': cardholder.id}), 201
