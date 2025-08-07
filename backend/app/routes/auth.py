
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from werkzeug.security import check_password_hash

from .. import db
from ..models import User

router = APIRouter()


@router.post("/login")
def login(data: dict, Authorize: AuthJWT = Depends()):
    """Authenticate a user and return a JWT token."""
    logger = logging.getLogger(__name__)
    logger.info("Login attempt for %s", data.get("email"))
    user = User.query.filter_by(email=data.get("email")).first()
    if user and check_password_hash(user.password, data.get("password", "")):
        token = Authorize.create_access_token(subject=str(user.id))
        logger.debug("Generated token for user %s", user.id)
        return {"access_token": token}
    logger.warning("Invalid login attempt for %s", data.get("email"))
    raise HTTPException(status_code=401, detail="invalid credentials")


@router.post("/register")
def register(payload: dict):
    """Register a new user."""
    logger = logging.getLogger(__name__)
    logger.info("Registering user %s", payload.get("email"))
    user = User(
        name=payload.get("name"),
        username=payload.get("username"),
        email=payload.get("email"),
    )
    user.set_password(payload.get("password", ""))
    db.session.add(user)
    db.session.commit()
    logger.debug("Created user id=%s", user.id)
    return {"id": user.id}
