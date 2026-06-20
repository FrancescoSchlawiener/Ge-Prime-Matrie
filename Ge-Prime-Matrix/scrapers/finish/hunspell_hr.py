"""Hunspell hr — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellHrScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("hr", download_url=download_url, name="hunspell_hr")
