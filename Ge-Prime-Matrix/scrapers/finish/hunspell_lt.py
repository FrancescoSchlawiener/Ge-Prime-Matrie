"""Hunspell lt — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellLtScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("lt", download_url=download_url, name="hunspell_lt")
