"""Romansh — Leipzig roh."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}roh_wikipedia_2021_10K.tar.gz"


class RomanshScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="romansh",
            language="rm",
            download_url=download_url or DEFAULT_URL,
            portal_lang="roh",
        )
