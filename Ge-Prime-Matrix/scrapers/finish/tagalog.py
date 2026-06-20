"""Tagalog — Leipzig tgl."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}tgl_wikipedia_2021_100K.tar.gz"


class TagalogScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="tagalog",
            language="tl",
            download_url=download_url or DEFAULT_URL,
            portal_lang="tgl",
        )
