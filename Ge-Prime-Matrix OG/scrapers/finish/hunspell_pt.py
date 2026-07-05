"""Hunspell pt — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellPtScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("pt", download_url=download_url, name="hunspell_pt")
