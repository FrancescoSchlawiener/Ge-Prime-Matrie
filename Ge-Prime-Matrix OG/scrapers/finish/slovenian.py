"""Slovenian — Leipzig slv."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}slv_wikipedia_2021_300K.tar.gz"


class SlovenianScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="slovenian",
            language="sl",
            download_url=download_url or DEFAULT_URL,
            portal_lang="slv",
        )
