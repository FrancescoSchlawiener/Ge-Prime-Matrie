"""Malay — Leipzig msa."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}msa_wikipedia_2021_300K.tar.gz"


class MalayScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="malay",
            language="ms",
            download_url=download_url or DEFAULT_URL,
            portal_lang="msa",
        )
