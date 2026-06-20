"""Luxembourgish — Leipzig ltz."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}ltz_wikipedia_2021_100K.tar.gz"


class LuxembourgishScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="luxembourgish",
            language="lb",
            download_url=download_url or DEFAULT_URL,
            portal_lang="ltz",
        )
