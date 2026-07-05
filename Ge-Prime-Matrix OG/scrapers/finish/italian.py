"""Italian — Leipzig ita."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}ita_wikipedia_2021_300K.tar.gz"


class ItalianScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="italian",
            language="it",
            download_url=download_url or DEFAULT_URL,
            portal_lang="ita",
        )
