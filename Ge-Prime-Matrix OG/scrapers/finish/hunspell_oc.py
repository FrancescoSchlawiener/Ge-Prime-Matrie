"""Hunspell oc — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellOcScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("oc", download_url=download_url, name="hunspell_oc")
