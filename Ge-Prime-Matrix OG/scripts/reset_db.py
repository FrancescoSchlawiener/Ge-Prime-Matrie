#!/usr/bin/env python3
"""Datenbank löschen und leer neu anlegen."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from db.repository import WordRepository  # Pfad: db.paths.default_db_path


def _print(msg: str) -> None:
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"))


def main() -> None:
    repo = WordRepository()
    repo.delete_database()
    repo.init_db()
    _print(f"Geloescht und neu erstellt: {repo.db_path.name} (data/)")
    repo.close()


if __name__ == "__main__":
    main()
