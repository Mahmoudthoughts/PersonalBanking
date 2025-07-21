from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os
from flask_migrate import Migrate

db = SQLAlchemy()
jwt = JWTManager()

from .routes import register_blueprints


def create_app(config_object="app.config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Enable CORS for all routes to allow the Angular frontend to access the API
    CORS(app)

    db.init_app(app)
    migrations_dir = os.path.join(os.path.dirname(__file__), '..', 'migrations')
    Migrate(app, db, directory=migrations_dir)
    jwt.init_app(app)
    register_blueprints(app)

    return app
