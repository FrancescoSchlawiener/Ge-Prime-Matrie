"""Skipped-word log — one TSV per scraper run."""

from __future__ import annotations

from pathlib import Path

_LOG_DIR = Path(__file__).resolve().parent / "logs"


class SkippedLog:
    """Append skipped words to scrapers/logs/skipped_<source>.tsv."""

    def __init__(self, source: str) -> None:
        _LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.path = _LOG_DIR / f"skipped_{source}.tsv"
        self._fh = self.path.open("w", encoding="utf-8", newline="\n")
        self._fh.write("word\tlanguage\treason\n")

    def write(self, word: str, language: str | None, reason: str) -> None:
        lang = (language or "random").strip().lower()
        safe_word = word.replace("\t", " ").replace("\n", " ").replace("\r", "")
        safe_reason = reason.replace("\t", " ").replace("\n", " ")
        self._fh.write(f"{safe_word}\t{lang}\t{safe_reason}\n")

    def close(self) -> None:
        self._fh.close()
