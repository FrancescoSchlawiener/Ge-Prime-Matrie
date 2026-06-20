"""Spanish — Leipzig spa."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}spa_wikipedia_2021_300K.tar.gz"


class SpanishScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="spanish",
            language="es",
            download_url=download_url or DEFAULT_URL,
            portal_lang="spa",
        )
