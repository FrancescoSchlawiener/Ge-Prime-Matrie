"""Swahili — Leipzig swa."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}swa_wikipedia_2021_100K.tar.gz"


class SwahiliScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="swahili",
            language="sw",
            download_url=download_url or DEFAULT_URL,
            portal_lang="swa",
        )
