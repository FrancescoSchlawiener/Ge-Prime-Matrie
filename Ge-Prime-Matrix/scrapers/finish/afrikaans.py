"""Afrikaans — Leipzig afr."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}afr_wikipedia_2021_300K.tar.gz"


class AfrikaansScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="afrikaans",
            language="af",
            download_url=download_url or DEFAULT_URL,
            portal_lang="afr",
        )
