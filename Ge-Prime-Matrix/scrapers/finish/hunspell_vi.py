"""Hunspell vi — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellViScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("vi", download_url=download_url, name="hunspell_vi")
