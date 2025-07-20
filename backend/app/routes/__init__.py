from flask import Blueprint

from .auth import bp as auth_bp

from .transactions import bp as transactions_bp
from .tags import bp as tags_bp
from .cardholders import bp as cardholders_bp

def register_blueprints(<<<< 1uru9u-codex/assist-with-task
    app.register_blueprint(transactions_bp)
    app.register_blueprint(tags_bp)
    app.register_blueprint(cardholders_bp)
