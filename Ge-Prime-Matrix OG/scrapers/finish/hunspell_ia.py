"""Hunspell ia — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellIaScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("ia", download_url=download_url, name="hunspell_ia")
