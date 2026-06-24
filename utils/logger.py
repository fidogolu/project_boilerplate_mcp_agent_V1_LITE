# utils/logger.py
"""Production-ready logging configuration.

Provides a singleton LOGGER instance with:
- Console output (stdout)
- File output (logs/app.log)
- Configurable log level via LOG_LEVEL env var
- Silenced third-party loggers

Import:
    from utils.logger import LOGGER
"""

import logging
import os
import sys


def get_logger() -> logging.Logger:
    """Get or create the application logger singleton."""
    logger = logging.getLogger("app")

    if logger.handlers:
        return logger

    logger.propagate = False

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(console_handler)

    # File Handler
    os.makedirs("logs", exist_ok=True)
    file_handler = logging.FileHandler("logs/app.log", encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(file_handler)

    # Log level from environment
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    # Silence noisy third-party loggers
    for noisy_logger in [
        "httpx",
        "httpcore",
        "openai",
        "langchain",
        "langgraph",
    ]:
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)

    return logger


LOGGER = get_logger()
