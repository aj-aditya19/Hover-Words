import logging
import os
import sys


def _log_dir():
    """Return a writable per-user folder for logs, e.g.
    C:\\Users\\<you>\\AppData\\Local\\HoverDictionary"""
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    path = os.path.join(base, "HoverDictionary")
    os.makedirs(path, exist_ok=True)
    return path


def get_logger():
    logger = logging.getLogger("hover_dictionary")
    if logger.handlers:
        return logger  # already configured

    logger.setLevel(logging.INFO)
    log_path = os.path.join(_log_dir(), "hover-dictionary.log")

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )
    logger.addHandler(file_handler)

    # Also print to console when one exists (dev mode / python main.py),
    # but stay silent when frozen with --noconsole (sys.stdout is None then).
    if sys.stdout is not None:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        logger.addHandler(stream_handler)

    return logger
