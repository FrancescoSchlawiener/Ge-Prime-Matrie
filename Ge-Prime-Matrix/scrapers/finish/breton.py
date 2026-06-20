"""Breton — Leipzig bre."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}bre_wikipedia_2021_100K.tar.gz"


class BretonScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="breton",
            language="br",
            download_url=download_url or DEFAULT_URL,
            portal_lang="bre",
        )
