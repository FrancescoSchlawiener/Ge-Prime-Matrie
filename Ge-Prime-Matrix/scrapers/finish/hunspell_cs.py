"""Hunspell cs — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellCsScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("cs", download_url=download_url, name="hunspell_cs")
