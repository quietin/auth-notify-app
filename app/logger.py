# app/logger.py
import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from app.config import BASE_DIR

LOG_DIR = BASE_DIR.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

def init_logging(level: int = logging.INFO) -> None:
    if logging.getLogger().hasHandlers():
        return

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s"
    )

    # Console handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    # Daily rotating file handler
    file_handler = TimedRotatingFileHandler(
        LOG_DIR / "app.log",
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8",
        utc=True
    )
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(stream_handler)
    root_logger.addHandler(file_handler)

    # supress warnings of passlib
    logging.getLogger('passlib').setLevel(logging.ERROR)
