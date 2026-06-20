"""Hunspell et — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellEtScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("et", download_url=download_url, name="hunspell_et")
