"""Hunspell fy — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellFyScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("fy", download_url=download_url, name="hunspell_fy")
