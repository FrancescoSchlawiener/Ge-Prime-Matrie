"""Alle Scraper-Quellen — Romanze + weitere lateinische Sprachen."""

from __future__ import annotations

from scrapers.latin_registry import LATIN_HUNSPELL, LATIN_SCRAPERS, LATIN_SOURCE_NAMES
from scrapers.romance_registry import ROMANCE_HUNSPELL, ROMANCE_SCRAPERS, ROMANCE_SOURCE_NAMES

ALL_SCRAPERS: dict[str, type] = {
    **ROMANCE_SCRAPERS,
    **LATIN_SCRAPERS,
}

LEIPZIG_SOURCE_NAMES: tuple[str, ...] = ROMANCE_SOURCE_NAMES + LATIN_SOURCE_NAMES

HUNSPELL_SOURCE_NAMES: tuple[str, ...] = tuple(
    name for name, _ in ROMANCE_HUNSPELL
) + tuple(name for name, _ in LATIN_HUNSPELL)
