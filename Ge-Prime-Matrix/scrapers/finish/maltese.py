"""Maltese — Leipzig mlt."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}mlt_wikipedia_2021_10K.tar.gz"


class MalteseScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="maltese",
            language="mt",
            download_url=download_url or DEFAULT_URL,
            portal_lang="mlt",
        )
