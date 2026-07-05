"""Hunspell eu — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellEuScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("eu", download_url=download_url, name="hunspell_eu")
