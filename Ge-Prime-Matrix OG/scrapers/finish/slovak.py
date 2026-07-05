"""Slovak — Leipzig slk."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}slk_wikipedia_2021_300K.tar.gz"


class SlovakScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="slovak",
            language="sk",
            download_url=download_url or DEFAULT_URL,
            portal_lang="slk",
        )
