"""Hunspell ro — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellRoScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("ro", download_url=download_url, name="hunspell_ro")
