"""Hunspell gd — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellGdScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("gd", download_url=download_url, name="hunspell_gd")
