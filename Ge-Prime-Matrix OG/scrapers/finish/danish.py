"""Danish — Leipzig dan."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}dan_wikipedia_2021_300K.tar.gz"


class DanishScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="danish",
            language="da",
            download_url=download_url or DEFAULT_URL,
            portal_lang="dan",
        )
