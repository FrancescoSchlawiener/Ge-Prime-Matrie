"""Lithuanian — Leipzig lit."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}lit_wikipedia_2021_300K.tar.gz"


class LithuanianScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="lithuanian",
            language="lt",
            download_url=download_url or DEFAULT_URL,
            portal_lang="lit",
        )
