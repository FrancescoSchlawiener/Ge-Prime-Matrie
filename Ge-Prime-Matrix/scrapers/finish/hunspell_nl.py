"""Hunspell nl — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellNlScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("nl", download_url=download_url, name="hunspell_nl")
