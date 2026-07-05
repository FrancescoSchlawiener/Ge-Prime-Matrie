"""French — Leipzig fra."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}fra_wikipedia_2021_300K.tar.gz"


class FrenchScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="french",
            language="fr",
            download_url=download_url or DEFAULT_URL,
            portal_lang="fra",
        )
