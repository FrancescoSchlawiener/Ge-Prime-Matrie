"""Friulanisch — Hunspell fur (wooorm)."""

from scrapers.hunspell import HunspellScraper


class FriulianScraper(HunspellScraper):
    def __init__(self, download_url: str | None = None):
        super().__init__("fur", download_url=download_url, name="friulian")
