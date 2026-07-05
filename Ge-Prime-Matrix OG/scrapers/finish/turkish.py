"""Turkish — Leipzig tur."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}tur_wikipedia_2021_300K.tar.gz"


class TurkishScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="turkish",
            language="tr",
            download_url=download_url or DEFAULT_URL,
            portal_lang="tur",
        )
