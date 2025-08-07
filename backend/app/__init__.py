from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate

from .log import setup_logging

db = SQLAlchemy()
jwt = JWTManager()

from .routes import register_blueprints
from .services.tag_ai import schedule_training, tag_ai


def create_app(config_object="app.config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Configure application-wide logging
    setup_logging()

    # Enable CORS for all routes to allow the Angular frontend to access the API
    CORS(app)

    db.init_app(app)
    Migrate(app, db)
    jwt.init_app(app)
    register_blueprints(app)

    # Train tag AI in the background using existing transactions
    with app.app_context():
        try:
            tag_ai.train()
        except Exception:  # pragma: no cover - startup training errors
            app.logger.exception("Initial TagAI training failed")
    schedule_training(app)

    return app
