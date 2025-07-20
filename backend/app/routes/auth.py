
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token

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
