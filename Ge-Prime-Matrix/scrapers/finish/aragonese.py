"""Aragonese — Leipzig arg."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}arg_wikipedia_2021_10K.tar.gz"


class AragoneseScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="aragonese",
            language="an",
            download_url=download_url or DEFAULT_URL,
            portal_lang="arg",
        )
