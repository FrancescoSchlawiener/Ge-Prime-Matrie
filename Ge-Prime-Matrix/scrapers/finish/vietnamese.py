"""Vietnamese — Leipzig vie."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}vie_wikipedia_2021_300K.tar.gz"


class VietnameseScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="vietnamese",
            language="vi",
            download_url=download_url or DEFAULT_URL,
            portal_lang="vie",
        )
