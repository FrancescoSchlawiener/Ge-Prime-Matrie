"""Sardinian — Leipzig srd."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}srd_wikipedia_2021_10K.tar.gz"


class SardinianScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="sardinian",
            language="srd",
            download_url=download_url or DEFAULT_URL,
            portal_lang="srd",
        )
