"""Hunspell eo — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellEoScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("eo", download_url=download_url, name="hunspell_eo")
