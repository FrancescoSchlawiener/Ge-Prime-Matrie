"""Hunspell ca — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellCaScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("ca", download_url=download_url, name="hunspell_ca")
