"""Hunspell cy — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellCyScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("cy", download_url=download_url, name="hunspell_cy")
