"""Hunspell is — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellIsScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("is", download_url=download_url, name="hunspell_is")
