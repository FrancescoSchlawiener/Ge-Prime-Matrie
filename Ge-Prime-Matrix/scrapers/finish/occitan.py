"""Occitan — Leipzig oci."""

from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

DEFAULT_URL = f"{LEIPZIG_BASE}oci_wikipedia_2021_100K.tar.gz"


class OccitanScraper(LeipzigLanguageScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__(
            name="occitan",
            language="oc",
            download_url=download_url or DEFAULT_URL,
            portal_lang="oci",
        )
