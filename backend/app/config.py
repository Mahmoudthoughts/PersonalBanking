import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me")
    # Default log level used by ``setup_logging``
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
