"""Indonesian — Leipzig ind."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}ind_wikipedia_2021_300K.tar.gz"


class IndonesianScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="indonesian",
            language="id",
            download_url=download_url or DEFAULT_URL,
            portal_lang="ind",
        )
