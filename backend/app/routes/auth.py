from flask import Blueprint, jsonify

bp = Blueprint('auth', __name__)


@bp.route('/auth/login', methods=['POST'])
def login():
    # Placeholder implementation
    return jsonify({'message': 'login'}), 200
