"""Hunspell it — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellItScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("it", download_url=download_url, name="hunspell_it")
