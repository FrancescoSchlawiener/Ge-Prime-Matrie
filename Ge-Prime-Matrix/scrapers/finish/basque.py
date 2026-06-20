"""Basque — Leipzig eus."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}eus_wikipedia_2021_300K.tar.gz"


class BasqueScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="basque",
            language="eu",
            download_url=download_url or DEFAULT_URL,
            portal_lang="eus",
        )
