from . import create_app, db
from .utils.line_logger import enable_line_logging

enable_line_logging()

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {"db": db}


if __name__ == "__main__":
    app.run(debug=True)
