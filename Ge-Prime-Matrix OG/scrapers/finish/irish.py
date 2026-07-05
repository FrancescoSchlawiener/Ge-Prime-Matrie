"""Irish — Leipzig gle."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}gle_wikipedia_2021_10K.tar.gz"


class IrishScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="irish",
            language="ga",
            download_url=download_url or DEFAULT_URL,
            portal_lang="gle",
        )
