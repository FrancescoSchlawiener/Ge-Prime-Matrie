"""Hunspell hu — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellHuScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("hu", download_url=download_url, name="hunspell_hu")
