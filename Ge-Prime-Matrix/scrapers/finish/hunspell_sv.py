"""Hunspell sv — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellSvScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("sv", download_url=download_url, name="hunspell_sv")
