"""Bosnian — Leipzig bos."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}bos_wikipedia_2021_300K.tar.gz"


class BosnianScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="bosnian",
            language="bs",
            download_url=download_url or DEFAULT_URL,
            portal_lang="bos",
        )
