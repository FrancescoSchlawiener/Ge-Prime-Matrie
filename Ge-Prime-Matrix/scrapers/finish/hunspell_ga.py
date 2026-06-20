"""Hunspell ga — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellGaScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("ga", download_url=download_url, name="hunspell_ga")
