"""Polish — Leipzig pol."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}pol_wikipedia_2021_300K.tar.gz"


class PolishScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="polish",
            language="pl",
            download_url=download_url or DEFAULT_URL,
            portal_lang="pol",
        )
