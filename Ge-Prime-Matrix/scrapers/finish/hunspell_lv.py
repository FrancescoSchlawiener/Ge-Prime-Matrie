"""Hunspell lv — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellLvScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("lv", download_url=download_url, name="hunspell_lv")
