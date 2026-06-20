"""Hunspell sk — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellSkScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("sk", download_url=download_url, name="hunspell_sk")
