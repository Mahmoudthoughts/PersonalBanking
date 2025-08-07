from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required

from .. import db
from ..models import Tag

bp = Blueprint('tags', __name__, url_prefix='/tags')


@bp.route('', methods=['GET'])
@jwt_required()
def list_tags():
    current_app.logger.debug('Listing tags')
    tags = Tag.query.all()
    return jsonify([
        {'id': t.id, 'name': t.name, 'parent_id': t.parent_id}
        for t in tags
    ])


@bp.route('', methods=['POST'])
@jwt_required()
def create_tag():
    payload = request.get_json() or {}
    current_app.logger.info('Creating tag %s', payload.get('name'))
    tag = Tag(name=payload['name'], parent_id=payload.get('parent_id'))
    db.session.add(tag)
    db.session.commit()
    current_app.logger.debug('Created tag id=%s', tag.id)
    return jsonify({'id': tag.id}), 201


@bp.route('/<int:tag_id>', methods=['PATCH'])
@jwt_required()
def update_tag(tag_id: int):
    """Update an existing tag."""
    current_app.logger.debug('Updating tag %s', tag_id)
    tag = Tag.query.get_or_404(tag_id)
    payload = request.get_json() or {}
    if 'name' in payload:
        tag.name = payload['name']
    if 'parent_id' in payload:
        tag.parent_id = payload['parent_id']
    db.session.commit()
    current_app.logger.info('Updated tag id=%s', tag.id)
    return jsonify({'id': tag.id})


@bp.route('/<int:tag_id>', methods=['DELETE'])
@jwt_required()
def delete_tag(tag_id: int):
    """Remove a tag."""
    current_app.logger.warning('Deleting tag %s', tag_id)
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    return jsonify({'status': 'deleted'})
