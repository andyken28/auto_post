import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(config):
    """Configure logging: console + rotating file handler into `logs/`.

    This keeps logging initialization centralized and can be expanded later
    for different environments.
    """
    log_dir = config.get("LOG_DIR") if isinstance(config, dict) else getattr(config, "LOG_DIR", None)
    if not log_dir:
        log_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "logs")

    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "app.log")

    root = logging.getLogger()
    if root.handlers:
        return  # already configured

    root.setLevel(logging.INFO)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
    root.addHandler(console)

    file_handler = RotatingFileHandler(log_path, maxBytes=10 * 1024 * 1024, backupCount=5)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    ))
    root.addHandler(file_handler)

    # Separate error log file
    error_path = os.path.join(log_dir, "error.log")
    error_handler = RotatingFileHandler(error_path, maxBytes=5 * 1024 * 1024, backupCount=3)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    ))
    root.addHandler(error_handler)
