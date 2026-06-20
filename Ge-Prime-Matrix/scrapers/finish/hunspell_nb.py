"""Hunspell nb — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellNbScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("nb", download_url=download_url, name="hunspell_nb")
