"""Hungarian — Leipzig hun."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}hun_wikipedia_2021_300K.tar.gz"


class HungarianScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="hungarian",
            language="hu",
            download_url=download_url or DEFAULT_URL,
            portal_lang="hun",
        )
