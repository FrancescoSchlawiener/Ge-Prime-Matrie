"""Armenian Normalisierung — NFC + uppercase."""

from __future__ import annotations

import unicodedata


def normalize_armenian(text: str) -> str:
    return unicodedata.normalize("NFC", text).upper()
