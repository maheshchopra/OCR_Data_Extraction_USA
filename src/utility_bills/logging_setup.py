import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(log_dir: str | Path, level: int = logging.INFO) -> logging.Logger:
    """
    Creates a logger that writes to console + logs/utility_bills.log (rotating).
    """
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("utility_bills")
    logger.setLevel(level)
    logger.propagate = False

    # Avoid duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(fmt)

    file_handler = RotatingFileHandler(
        filename=str(log_dir / "utility_bills.log"),
        maxBytes=2_000_000,  # ~2MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(fmt)

    logger.addHandler(console)
    logger.addHandler(file_handler)
    return logger
