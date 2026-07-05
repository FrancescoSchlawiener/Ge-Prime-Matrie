#!/usr/bin/env python3
"""CLI to scrape word lists into the Ge-Prime SQLite database."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from db.repository import WordRepository
from scrapers.finish.aspell import AspellScraper
from scrapers.finish.friulian import FriulianScraper
from scrapers.github import GitHubScraper
from scrapers.finish.kevina import KevinaScraper
from scrapers.leipzig import LeipzigScraper
from scrapers.finish.local import LocalFileScraper
from scrapers.latin_registry import LATIN_HUNSPELL, LATIN_SOURCE_NAMES
from scrapers.romance_registry import ROMANCE_HUNSPELL, ROMANCE_SOURCE_NAMES
from scrapers.sources_registry import ALL_SCRAPERS

_SOURCE_CHOICES = [
    "leipzig",
    "aspell",
    "kevina",
    "github",
    *ROMANCE_SOURCE_NAMES,
    *(name for name, _ in ROMANCE_HUNSPELL),
    "friulian",
    *LATIN_SOURCE_NAMES,
    *(name for name, _ in LATIN_HUNSPELL),
    "romance",
    "romance_hunspell",
    "europe",
    "europe_hunspell",
    "intl",
    "all",
]


def _build_scrapers(args: argparse.Namespace) -> list:
    scrapers = []
    if args.file:
        scrapers.append(LocalFileScraper(args.file, language=args.lang))
        return scrapers
    if args.source in ("leipzig", "all"):
        scrapers.append(LeipzigScraper(download_url=args.url))
    if args.source in ("kevina", "all"):
        scrapers.append(KevinaScraper())
    if args.source in ("aspell", "all"):
        scrapers.append(AspellScraper(language=args.lang))
    if args.source == "romance":
        for name in ROMANCE_SOURCE_NAMES:
            scrapers.append(ALL_SCRAPERS[name]())
    elif args.source == "romance_hunspell":
        for name, _ in ROMANCE_HUNSPELL:
            scrapers.append(ALL_SCRAPERS[name]())
        scrapers.append(FriulianScraper())
    elif args.source == "europe":
        for name in LATIN_SOURCE_NAMES:
            scrapers.append(ALL_SCRAPERS[name]())
    elif args.source == "europe_hunspell":
        for name, _ in LATIN_HUNSPELL:
            scrapers.append(ALL_SCRAPERS[name]())
    elif args.source in ("intl",):
        for name in ROMANCE_SOURCE_NAMES:
            scrapers.append(ALL_SCRAPERS[name]())
        for name in LATIN_SOURCE_NAMES:
            scrapers.append(ALL_SCRAPERS[name]())
    elif args.source in ALL_SCRAPERS:
        scrapers.append(ALL_SCRAPERS[args.source]())
    if args.source == "github":
        if not args.url:
            print("Error: --url required for github source", file=sys.stderr)
            sys.exit(1)
        scrapers.append(
            GitHubScraper(args.url, language=args.lang, source_name="github")
        )
    return scrapers


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape word lists into Ge-Prime DB")
    parser.add_argument(
        "--source",
        choices=_SOURCE_CHOICES,
        default="leipzig",
        help="Word list source",
    )
    parser.add_argument("--url", help="Download URL override (leipzig/github)")
    parser.add_argument("--file", help="Local word list file (one word per line)")
    parser.add_argument("--lang", help="ISO language code override")
    parser.add_argument(
        "--db",
        help="Nur für Tests — Standard: data/ge_prime.db (siehe db/paths.py)",
    )
    args = parser.parse_args()

    scrapers = _build_scrapers(args)
    if not scrapers:
        print("No scrapers selected.", file=sys.stderr)
        sys.exit(1)

    repo = WordRepository(args.db) if args.db else WordRepository()
    repo.init_db()

    for scraper in scrapers:
        print(f"Scraping {scraper.name}...")
        result = scraper.scrape_to_db(repo)
        print(
            f"  fetched={result.fetched} accepted={result.accepted} "
            f"skipped={result.skipped} inserted={result.inserted} "
            f"duplicates={result.duplicates}"
        )
        if result.skipped_log and result.skipped:
            print(f"  skip-log: scrapers/logs/{Path(result.skipped_log).name}")
        for err in result.errors:
            print(f"  ERROR: {err}")

    print(f"\nTotal words in DB: {repo.total_count()}")
    repo.close()


if __name__ == "__main__":
    main()
