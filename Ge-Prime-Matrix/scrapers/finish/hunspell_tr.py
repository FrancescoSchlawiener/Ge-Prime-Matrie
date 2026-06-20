"""Hunspell tr — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellTrScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("tr", download_url=download_url, name="hunspell_tr")
