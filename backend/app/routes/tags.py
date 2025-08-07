import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT

from .. import db
from ..models import Tag


router = APIRouter()


@router.get("")
def list_tags(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    logger = logging.getLogger(__name__)
    logger.debug('Listing tags')
    tags = Tag.query.all()
    return [
        {'id': t.id, 'name': t.name, 'parent_id': t.parent_id}
        for t in tags
    ]


@router.post("")
def create_tag(payload: dict, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    logger = logging.getLogger(__name__)
    logger.info('Creating tag %s', payload.get('name'))
    tag = Tag(name=payload['name'], parent_id=payload.get('parent_id'))
    db.session.add(tag)
    db.session.commit()
    logger.debug('Created tag id=%s', tag.id)
    return {'id': tag.id}


@router.patch("/{tag_id}")
def update_tag(tag_id: int, payload: dict, Authorize: AuthJWT = Depends()):
    """Update an existing tag."""
    Authorize.jwt_required()
    logger = logging.getLogger(__name__)
    logger.debug('Updating tag %s', tag_id)
    tag = Tag.query.get(tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail='tag not found')
    if 'name' in payload:
        tag.name = payload['name']
    if 'parent_id' in payload:
        tag.parent_id = payload['parent_id']
    db.session.commit()
    logger.info('Updated tag id=%s', tag.id)
    return {'id': tag.id}


@router.delete("/{tag_id}")
def delete_tag(tag_id: int, Authorize: AuthJWT = Depends()):
    """Remove a tag."""
    Authorize.jwt_required()
    logger = logging.getLogger(__name__)
    logger.warning('Deleting tag %s', tag_id)
    tag = Tag.query.get(tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail='tag not found')
    db.session.delete(tag)
    db.session.commit()
    return {'status': 'deleted'}
