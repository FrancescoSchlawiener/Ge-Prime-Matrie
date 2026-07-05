"""Catalan — Leipzig cat."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}cat_wikipedia_2021_300K.tar.gz"


class CatalanScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="catalan",
            language="ca",
            download_url=download_url or DEFAULT_URL,
            portal_lang="cat",
        )
