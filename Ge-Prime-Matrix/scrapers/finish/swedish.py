"""Swedish — Leipzig swe."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}swe_wikipedia_2021_300K.tar.gz"


class SwedishScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="swedish",
            language="sv",
            download_url=download_url or DEFAULT_URL,
            portal_lang="swe",
        )
