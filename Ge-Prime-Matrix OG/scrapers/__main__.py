"""Interactive CLI: python -m scrapers (from Ge-Prime-Matrix root)."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from db.repository import WordRepository
from scrapers.leipzig import LeipzigScraper
from scrapers.log import get_logger, setup_logging

# DB-Pfad: db.paths.default_db_path — WordRepository() ohne db_path= nutzen

from scrapers.romance_registry import ROMANCE_HUNSPELL, ROMANCE_SOURCE_NAMES

_FINISHED = (
    "kevina",
    "aspell",
    "local",
    *ROMANCE_SOURCE_NAMES,
    *(name for name, _ in ROMANCE_HUNSPELL),
)


def _print_result(result) -> None:
    print("\n--- ERGEBNIS ---")
    print(f"Quelle:    {result.source}")
    print(f"Gefunden:  {result.fetched}")
    print(f"Akzeptiert:{result.accepted}")
    print(f"Eingefügt: {result.inserted}")
    print(f"Duplikate: {result.duplicates}")
    print(f"Skipped:   {result.skipped}")
    if result.skipped_log and result.skipped:
        rel = Path(result.skipped_log).name
        print(f"Skip-Log:  scrapers/logs/{rel}")
    if result.errors:
        print(f"Fehler:    {result.errors}")


def main() -> None:
    setup_logging()
    logger = get_logger("cli")

    repo = WordRepository()
    repo.init_db()

    print("Welcher Scraper soll laufen?")
    print("1: Leipzig (DE Wikipedia)")
    print()
    print("Fertig importiert (scrapers/finish/):")
    for name in _FINISHED:
        print(f"  - {name}")

    choice = input("Auswahl (1): ").strip() or "1"

    if choice == "1":
        scraper = LeipzigScraper()
    else:
        print("Ungültige Auswahl. Nur Leipzig ist noch aktiv.")
        logger.error("Invalid menu choice: %r", choice)
        sys.exit(1)

    print(f"Starte Scraper '{scraper.name}'...")
    result = scraper.scrape_to_db(repo)
    _print_result(result)
    print(f"\nWörter in DB: {repo.total_count()}")
    repo.close()


if __name__ == "__main__":
    main()
