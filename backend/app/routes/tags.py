from flask import Blueprint, request, jsonify

from .. import db
from ..models import Tag

bp = Blueprint('tags', __name__, url_prefix='/tags')


@bp.route('', methods=['GET'])
def list_tags():
    tags = Tag.query.all()
    return jsonify([
        {'id': t.id, 'name': t.name, 'parent_id': t.parent_id}
        for t in tags
    ])


@bp.route('', methods=['POST'])
def create_tag():
    payload = request.get_json() or {}
    tag = Tag(name=payload['name'], parent_id=payload.get('parent_id'))
    db.session.add(tag)
    db.session.commit()
    return jsonify({'id': tag.id}), 201
