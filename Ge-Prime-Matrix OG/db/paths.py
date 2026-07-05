"""Einzige Quelle für den SQLite-Pfad — Web, CLI, Scraper, Tests.

NICHT hier abweichen:
  - kein ``gpm_words.db`` im Projektroot
  - kein zweiter Hardcode in scrapers/ oder web/
  - Override nur via Umgebungsvariable ``GE_PRIME_DB``

Standard: ``data/ge_prime.db`` (relativ zum Ge-Prime-Matrix-Root).
"""

from __future__ import annotations

import os
from pathlib import Path

# Ge-Prime-Matrix-Root (übergeordnet von db/)
ROOT = Path(__file__).resolve().parent.parent

# Relativer Standard — eine Datei für alles
DEFAULT_DB_RELATIVE = Path("data") / "ge_prime.db"


def default_db_path() -> Path:
    """Pfad zur Wort-Datenbank. Einzige autoritative Definition."""
    raw = os.environ.get("GE_PRIME_DB", "").strip()
    if raw:
        return Path(raw).expanduser().resolve()
    return (ROOT / DEFAULT_DB_RELATIVE).resolve()
