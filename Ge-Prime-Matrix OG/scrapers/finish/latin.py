"""Latin — Leipzig lat."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}lat_wikipedia_2021_100K.tar.gz"


class LatinScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="latin",
            language="la",
            download_url=download_url or DEFAULT_URL,
            portal_lang="lat",
        )
