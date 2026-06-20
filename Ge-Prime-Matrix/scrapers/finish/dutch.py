"""Dutch — Leipzig nld."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}nld_wikipedia_2021_300K.tar.gz"


class DutchScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="dutch",
            language="nl",
            download_url=download_url or DEFAULT_URL,
            portal_lang="nld",
        )
