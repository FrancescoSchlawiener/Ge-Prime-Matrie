"""Logging for scrapers — errors to file, no per-word spam."""

from __future__ import annotations

import logging
from pathlib import Path

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scrapers.base import ScrapeResult

LOGGER_NAME = "ge_prime.scrapers"
_LOG_DIR = Path(__file__).resolve().parent / "logs"
_LOG_FILE = _LOG_DIR / "scrape.log"

_configured = False


def setup_logging() -> None:
    """Configure scraper logging: ERROR to file, WARNING to console."""
    global _configured
    if _configured:
        return

    _LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    logger.propagate = False

    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

    file_handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(fmt)
    logger.addHandler(console_handler)

    _configured = True


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a child logger under ge_prime.scrapers."""
    if not _configured:
        setup_logging()
    if name:
        return logging.getLogger(f"{LOGGER_NAME}.{name}")
    return logging.getLogger(LOGGER_NAME)


def log_scrape_summary(scraper_name: str, result: "ScrapeResult") -> None:
    """Write a single summary line to the log file (INFO, not per-word)."""
    logger = get_logger()
    summary = (
        f"{scraper_name}: fetched={result.fetched} accepted={result.accepted} "
        f"skipped={result.skipped} inserted={result.inserted} "
        f"duplicates={result.duplicates} errors={len(result.errors)}"
    )
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            record = logging.LogRecord(
                name=logger.name,
                level=logging.INFO,
                pathname=__file__,
                lineno=0,
                msg=summary,
                args=(),
                exc_info=None,
            )
            if record.levelno >= handler.level:
                handler.handle(record)
