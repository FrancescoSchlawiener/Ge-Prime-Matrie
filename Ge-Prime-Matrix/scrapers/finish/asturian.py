"""Asturian — Leipzig ast."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}ast_wikipedia_2021_300K.tar.gz"


class AsturianScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="asturian",
            language="ast",
            download_url=download_url or DEFAULT_URL,
            portal_lang="ast",
        )
