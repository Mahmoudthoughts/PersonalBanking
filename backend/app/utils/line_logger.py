import os
import sys
import linecache
import logging
import threading

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _trace(frame, event, arg):
    if event == "line":
        filename = frame.f_code.co_filename
        if filename.startswith(BASE_PATH) and filename != __file__:
            lineno = frame.f_lineno
            func_name = frame.f_code.co_name
            code_line = linecache.getline(filename, lineno).strip()
            rel_path = os.path.relpath(filename, BASE_PATH)
            logging.debug("%s:%d in %s: %s", rel_path, lineno, func_name, code_line)
    return _trace


def enable_line_logging():
    """Enable logging of every executed line within the project."""
    logging.basicConfig(level=logging.DEBUG)
    sys.settrace(_trace)
    threading.settrace(_trace)
