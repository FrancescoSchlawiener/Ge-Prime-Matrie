"""Icelandic — Leipzig isl."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}isl_wikipedia_2021_100K.tar.gz"


class IcelandicScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="icelandic",
            language="is",
            download_url=download_url or DEFAULT_URL,
            portal_lang="isl",
        )
