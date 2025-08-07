from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel

from .log import setup_logging
from .routes import register_routers


db = SQLAlchemy()


class Settings(BaseModel):
    authjwt_secret_key: str = "change-me"


@AuthJWT.load_config
def get_config():
    return Settings()


def create_app(config_object: str | None = None) -> FastAPI:
    setup_logging()
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_routers(app)
    return app
