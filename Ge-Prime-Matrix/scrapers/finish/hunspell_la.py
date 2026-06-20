"""Hunspell la — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellLaScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("la", download_url=download_url, name="hunspell_la")
