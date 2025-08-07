from . import create_app
from .utils.line_logger import enable_line_logging

enable_line_logging()

app = create_app()

