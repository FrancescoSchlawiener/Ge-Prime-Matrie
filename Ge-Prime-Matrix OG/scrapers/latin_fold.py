"""Diakritika entfernen — Wörter auf A–Z (+ ß) abbilden."""

from __future__ import annotations

import unicodedata


def fold_latin(word: str) -> str:
    """NFKD + Combining Marks streichen (ñ→n, é→e, ç→c, …)."""
    decomposed = unicodedata.normalize("NFKD", word)
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
