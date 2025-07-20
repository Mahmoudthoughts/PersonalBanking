
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token

from .. import db
from ..models import User
 

bp = Blueprint('auth', __name__)


@bp.route('/auth/login', methods=['POST'])
def login():

    data = request.get_json() or {}
    user = User.query.filter_by(email=data.get('email')).first()
    if user and check_password_hash(user.password, data.get('password', '')):
        token = create_access_token(identity=user.id)
        return jsonify({'access_token': token}), 200
    return jsonify({'error': 'invalid credentials'}), 401


@bp.route('/auth/register', methods=['POST'])
def register():
    """Register a new user."""
    payload = request.get_json() or {}
    user = User(
        name=payload.get('name'),
        username=payload.get('username'),
        email=payload.get('email'),
    )
    user.set_password(payload.get('password', ''))
    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id}), 201
