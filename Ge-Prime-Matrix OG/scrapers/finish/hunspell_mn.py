"""Hunspell mn — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellMnScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("mn", download_url=download_url, name="hunspell_mn")
