from pathlib import Path
from typing import Iterable

from scrapers.base import WordListScraper


class LocalFileScraper(WordListScraper):
    """Read words from a local text file (one word per line)."""

    name = "local"

    def __init__(self, path: str | Path, language: str | None = None):
        self.path = Path(path)
        self.language = language
        self.url = str(self.path.resolve())

    def fetch_lines(self) -> Iterable[tuple[str, str | None]]:
        with self.path.open(encoding="utf-8", errors="replace") as fh:
            for line in fh:
                word = line.strip()
                if word and not word.startswith("#"):
                    yield word, self.language
