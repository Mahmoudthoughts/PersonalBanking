import logging

from fastapi import APIRouter, Depends
from fastapi_jwt_auth import AuthJWT

from .. import db
from ..models import Cardholder


router = APIRouter()


@router.get("")
def list_cardholders(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    logger = logging.getLogger(__name__)
    logger.debug('Listing cardholders')
    cardholders = Cardholder.query.all()
    return [
        {'id': c.id, 'name': c.name, 'color': c.color}
        for c in cardholders
    ]


@router.post("")
def create_cardholder(payload: dict, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    logger = logging.getLogger(__name__)
    logger.info('Creating cardholder %s', payload.get('name'))
    cardholder = Cardholder(name=payload['name'], color=payload.get('color'))
    db.session.add(cardholder)
    db.session.commit()
    logger.debug('Created cardholder id=%s', cardholder.id)
    return {'id': cardholder.id}
