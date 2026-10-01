import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

import structlog


def configure_logging(level: str = "INFO") -> None:
    log_file = Path(__file__).resolve().parents[2] / "logs" / "applications" / "application.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter("%(message)s")
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    file_handler = RotatingFileHandler(log_file, maxBytes=10_000_000, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(level.upper())
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
