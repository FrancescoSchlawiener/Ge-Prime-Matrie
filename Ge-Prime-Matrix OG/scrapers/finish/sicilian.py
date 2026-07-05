"""Sicilian — Leipzig scn."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}scn_wikipedia_2021_10K.tar.gz"


class SicilianScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="sicilian",
            language="scn",
            download_url=download_url or DEFAULT_URL,
            portal_lang="scn",
        )
