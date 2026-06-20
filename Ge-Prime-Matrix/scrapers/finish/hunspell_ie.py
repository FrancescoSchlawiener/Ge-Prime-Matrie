"""Hunspell ie — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellIeScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("ie", download_url=download_url, name="hunspell_ie")
