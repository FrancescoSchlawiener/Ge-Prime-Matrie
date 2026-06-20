"""Romanische Sprachen — Import aus scrapers/finish/."""

from __future__ import annotations

from scrapers.finish.catalan import CatalanScraper
from scrapers.finish.friulian import FriulianScraper
from scrapers.finish.french import FrenchScraper
from scrapers.finish.galician import GalicianScraper
from scrapers.finish.hunspell_ca import HunspellCaScraper
from scrapers.finish.hunspell_es import HunspellEsScraper
from scrapers.finish.hunspell_fr import HunspellFrScraper
from scrapers.finish.hunspell_fur import HunspellFurScraper
from scrapers.finish.hunspell_gl import HunspellGlScraper
from scrapers.finish.hunspell_it import HunspellItScraper
from scrapers.finish.hunspell_la import HunspellLaScraper
from scrapers.finish.hunspell_oc import HunspellOcScraper
from scrapers.finish.hunspell_pt import HunspellPtScraper
from scrapers.finish.hunspell_ro import HunspellRoScraper
from scrapers.finish.italian import ItalianScraper
from scrapers.finish.latin import LatinScraper
from scrapers.finish.occitan import OccitanScraper
from scrapers.finish.portuguese import PortugueseScraper
from scrapers.finish.romanian import RomanianScraper
from scrapers.finish.romansh import RomanshScraper
from scrapers.finish.spanish import SpanishScraper

ROMANCE_LEIPZIG: tuple[tuple[str, str, str, str], ...] = (
    ("spanish", "es", "spa", "spa_wikipedia_2021_300K"),
    ("french", "fr", "fra", "fra_wikipedia_2021_300K"),
    ("italian", "it", "ita", "ita_wikipedia_2021_300K"),
    ("portuguese", "pt", "por", "por_wikipedia_2021_300K"),
    ("romanian", "ro", "ron", "ron_wikipedia_2021_300K"),
    ("catalan", "ca", "cat", "cat_wikipedia_2021_300K"),
    ("galician", "gl", "glg", "glg_wikipedia_2021_300K"),
    ("occitan", "oc", "oci", "oci_wikipedia_2021_100K"),
    ("latin", "la", "lat", "lat_wikipedia_2021_100K"),
    ("romansh", "rm", "roh", "roh_wikipedia_2021_10K"),
)

ROMANCE_HUNSPELL: tuple[tuple[str, str], ...] = (
    ("hunspell_es", "es"),
    ("hunspell_fr", "fr"),
    ("hunspell_it", "it"),
    ("hunspell_pt", "pt"),
    ("hunspell_ca", "ca"),
    ("hunspell_gl", "gl"),
    ("hunspell_oc", "oc"),
    ("hunspell_ro", "ro"),
    ("hunspell_la", "la"),
    ("hunspell_fur", "fur"),
)

ROMANCE_SCRAPERS: dict[str, type] = {
    "spanish": SpanishScraper,
    "french": FrenchScraper,
    "italian": ItalianScraper,
    "portuguese": PortugueseScraper,
    "romanian": RomanianScraper,
    "catalan": CatalanScraper,
    "galician": GalicianScraper,
    "occitan": OccitanScraper,
    "latin": LatinScraper,
    "romansh": RomanshScraper,
    "hunspell_es": HunspellEsScraper,
    "hunspell_fr": HunspellFrScraper,
    "hunspell_it": HunspellItScraper,
    "hunspell_pt": HunspellPtScraper,
    "hunspell_ca": HunspellCaScraper,
    "hunspell_gl": HunspellGlScraper,
    "hunspell_oc": HunspellOcScraper,
    "hunspell_ro": HunspellRoScraper,
    "hunspell_la": HunspellLaScraper,
    "hunspell_fur": HunspellFurScraper,
    "friulian": FriulianScraper,
}

ROMANCE_SOURCE_NAMES: tuple[str, ...] = tuple(
    name for name, _, _, _ in ROMANCE_LEIPZIG
)
