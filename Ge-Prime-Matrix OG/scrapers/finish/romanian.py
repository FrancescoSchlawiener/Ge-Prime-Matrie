"""Romanian — Leipzig ron."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}ron_wikipedia_2021_300K.tar.gz"


class RomanianScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="romanian",
            language="ro",
            download_url=download_url or DEFAULT_URL,
            portal_lang="ron",
        )
