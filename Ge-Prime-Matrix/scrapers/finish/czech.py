"""Czech — Leipzig ces."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}ces_wikipedia_2021_300K.tar.gz"


class CzechScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="czech",
            language="cs",
            download_url=download_url or DEFAULT_URL,
            portal_lang="ces",
        )
