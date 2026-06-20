"""Hunspell lb — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellLbScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("lb", download_url=download_url, name="hunspell_lb")
