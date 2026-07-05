"""Hunspell sl — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellSlScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("sl", download_url=download_url, name="hunspell_sl")
