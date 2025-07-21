from flask import Blueprint

from .auth import bp as auth_bp
from .transactions import bp as transactions_bp
from .tags import bp as tags_bp
from .cardholders import bp as cardholders_bp
from .reports import bp as reports_bp


def register_blueprints(app: Blueprint) -> None:
    """Register all route blueprints with the given Flask app."""
    app.register_blueprint(auth_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(tags_bp)
    app.register_blueprint(cardholders_bp)
    app.register_blueprint(reports_bp)
