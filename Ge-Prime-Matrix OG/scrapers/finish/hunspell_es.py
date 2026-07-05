"""Hunspell es — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellEsScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("es", download_url=download_url, name="hunspell_es")
