from fastapi import FastAPI

from .auth import router as auth_router
from .transactions import router as transactions_router
from .tags import router as tags_router
from .cardholders import router as cardholders_router
from .reports import router as reports_router
from .genai import router as genai_router


def register_routers(app: FastAPI) -> None:
    """Register all API routers with the given FastAPI app."""
    app.include_router(auth_router, prefix="/auth")
    app.include_router(transactions_router, prefix="/transactions")
    app.include_router(tags_router, prefix="/tags")
    app.include_router(cardholders_router, prefix="/cardholders")
    app.include_router(reports_router, prefix="/reports")
    app.include_router(genai_router, prefix="/genai")
