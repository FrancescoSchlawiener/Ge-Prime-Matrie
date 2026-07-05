"""Welsh — Leipzig cym."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}cym_wikipedia_2021_100K.tar.gz"


class WelshScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="welsh",
            language="cy",
            download_url=download_url or DEFAULT_URL,
            portal_lang="cym",
        )
