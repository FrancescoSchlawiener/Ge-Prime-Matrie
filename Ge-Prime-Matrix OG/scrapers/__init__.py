from scrapers.base import ScrapeResult, WordListScraper
from scrapers.finish.aspell import AspellScraper
from scrapers.finish.kevina import KevinaScraper
from scrapers.finish.local import LocalFileScraper
from scrapers.hunspell import HunspellScraper
from scrapers.leipzig import LeipzigScraper
from scrapers.latin_registry import LATIN_SCRAPERS, LATIN_SOURCE_NAMES
from scrapers.romance_registry import ROMANCE_SCRAPERS, ROMANCE_SOURCE_NAMES
from scrapers.sources_registry import ALL_SCRAPERS

__all__ = [
    "ALL_SCRAPERS",
    "AspellScraper",
    "HunspellScraper",
    "KevinaScraper",
    "LATIN_SCRAPERS",
    "LATIN_SOURCE_NAMES",
    "LeipzigScraper",
    "LocalFileScraper",
    "ROMANCE_SCRAPERS",
    "ROMANCE_SOURCE_NAMES",
    "ScrapeResult",
    "WordListScraper",
]
