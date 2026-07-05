"""Hunspell pl — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellPlScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("pl", download_url=download_url, name="hunspell_pl")
