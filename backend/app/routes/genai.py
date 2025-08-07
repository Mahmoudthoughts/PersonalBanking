"""Routes for interacting with the generative AI service."""

import logging

from fastapi import APIRouter, Depends
from fastapi_jwt_auth import AuthJWT

from ..services.genai import run_prompt


router = APIRouter()


@router.post("/run")
def run_genai(payload: dict, Authorize: AuthJWT = Depends()):
    """Execute a prompt using the OpenAI Agents runner."""
    Authorize.jwt_required()
    logger = logging.getLogger(__name__)
    logger.debug("Running genai prompt")
    prompt = payload.get("prompt", "")
    result = run_prompt(prompt)
    return {"result": result}

