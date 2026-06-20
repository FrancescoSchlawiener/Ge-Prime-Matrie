"""Hunspell da — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellDaScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("da", download_url=download_url, name="hunspell_da")
