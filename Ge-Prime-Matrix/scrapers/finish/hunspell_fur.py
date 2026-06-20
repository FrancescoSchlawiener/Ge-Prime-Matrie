"""Hunspell fur — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellFurScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("fur", download_url=download_url, name="hunspell_fur")
