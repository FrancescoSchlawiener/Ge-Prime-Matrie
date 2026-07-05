"""Croatian — Leipzig hrv."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}hrv_wikipedia_2021_300K.tar.gz"


class CroatianScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="croatian",
            language="hr",
            download_url=download_url or DEFAULT_URL,
            portal_lang="hrv",
        )
