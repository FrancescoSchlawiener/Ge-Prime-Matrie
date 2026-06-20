"""Einzelne Sprach-Skripte aus latin_registry erzeugen."""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from scrapers.latin_registry import LATIN_HUNSPELL, LATIN_LEIPZIG

root = Path(__file__).resolve().parent

for name, lang, portal, _corpus in LATIN_LEIPZIG:
    cls = "".join(p.title() for p in name.split("_")) + "Scraper"
    (root / f"{name}.py").write_text(
        f'"""{name.title()} ({lang}) — Leipzig {portal}."""\n\n'
        f"from scrapers.latin_registry import {cls}\n\n"
        f'__all__ = ["{cls}"]\n',
        encoding="utf-8",
    )

for src, code in LATIN_HUNSPELL:
    path = root / f"{src}.py"
    cls = "".join(p.title() for p in src.split("_")) + "Scraper"
    path.write_text(
        f'"""Hunspell {code}."""\n\n'
        "from scrapers.hunspell import HunspellScraper\n\n\n"
        f"class {cls}(HunspellScraper):\n"
        "    def __init__(self, download_url: str | None = None):\n"
        f'        super().__init__("{code}", download_url=download_url, name="{src}")\n',
        encoding="utf-8",
    )

print("leipzig", len(LATIN_LEIPZIG), "hunspell", len(LATIN_HUNSPELL))
