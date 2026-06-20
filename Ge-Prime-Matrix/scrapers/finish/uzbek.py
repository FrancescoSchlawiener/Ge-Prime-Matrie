"""Uzbek — Leipzig uzb."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}uzb_wikipedia_2021_100K.tar.gz"


class UzbekScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="uzbek",
            language="uz",
            download_url=download_url or DEFAULT_URL,
            portal_lang="uzb",
        )
