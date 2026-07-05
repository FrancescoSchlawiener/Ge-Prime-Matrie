"""Zentralisierte DB-Pfade — GPM greift nur auf die geklonte Roman-Alpha-DB zu."""

from __future__ import annotations

from pathlib import Path

FUNCTIONS_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = FUNCTIONS_ROOT / "data"
GPM_ROMAN_ALPHA_DB = DATA_DIR / "ge_prime_roman_alpha_alt.db"
OG_DB_READONLY = FUNCTIONS_ROOT.parent.parent / "Ge-Prime-Matrix OG" / "data" / "ge_prime.db"
