"""Hunspell gl — wooorm/dictionaries."""

from scrapers.hunspell import HunspellScraper


class HunspellGlScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("gl", download_url=download_url, name="hunspell_gl")
