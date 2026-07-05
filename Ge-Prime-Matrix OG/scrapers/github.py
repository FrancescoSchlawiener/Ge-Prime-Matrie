from typing import Iterable

import requests

from scrapers.base import WordListScraper


class GitHubScraper(WordListScraper):
    """Fetch a raw text word list from any URL (e.g. GitHub raw)."""

    name = "github"

    def __init__(
        self,
        url: str,
        language: str | None = None,
        source_name: str | None = None,
    ):
        self.url = url
        self.language = language
        self.name = source_name or "github"

    def fetch_lines(self) -> Iterable[tuple[str, str | None]]:
        resp = requests.get(self.url, timeout=120)
        resp.raise_for_status()
        for line in resp.text.splitlines():
            word = line.strip()
            if word and not word.startswith("#"):
                yield word, self.language
