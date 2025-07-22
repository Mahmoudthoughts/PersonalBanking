import logging
from logging.handlers import RotatingFileHandler

from .config import Config


def setup_logging():
    """Configure root logger with a rotating file handler."""
    log_level = getattr(logging, getattr(Config, "LOG_LEVEL", "INFO"), logging.INFO)
    handler = RotatingFileHandler('app.log', maxBytes=10_000_000, backupCount=5)
    handler.setFormatter(
        logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    handler.setLevel(log_level)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)
