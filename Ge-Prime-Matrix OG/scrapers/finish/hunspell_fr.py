"""Hunspell fr — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellFrScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("fr", download_url=download_url, name="hunspell_fr")
