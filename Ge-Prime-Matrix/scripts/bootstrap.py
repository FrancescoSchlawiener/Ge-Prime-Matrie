#!/usr/bin/env python3
"""Initialize empty database (no seed data)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from db.repository import WordRepository


def bootstrap() -> None:
    repo = WordRepository()
    repo.init_db()
    print("Datenbank bereit (leer, wenn neu).")
    print("Sprache: Web = Random/unsortiert · Scraper = ISO-Code wenn bekannt.")
    repo.close()


if __name__ == "__main__":
    bootstrap()
