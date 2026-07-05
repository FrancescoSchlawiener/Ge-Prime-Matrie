"""Galician — Leipzig glg."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}glg_wikipedia_2021_300K.tar.gz"


class GalicianScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="galician",
            language="gl",
            download_url=download_url or DEFAULT_URL,
            portal_lang="glg",
        )
