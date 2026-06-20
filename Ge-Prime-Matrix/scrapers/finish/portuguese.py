"""Portuguese — Leipzig por."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}por_wikipedia_2021_300K.tar.gz"


class PortugueseScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="portuguese",
            language="pt",
            download_url=download_url or DEFAULT_URL,
            portal_lang="por",
        )
