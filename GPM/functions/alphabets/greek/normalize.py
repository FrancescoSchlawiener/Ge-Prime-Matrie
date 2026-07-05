"""Greek Normalisierung — NFC + Uppercase."""

from __future__ import annotations

import unicodedata


def normalize_greek(text: str) -> str:
    return unicodedata.normalize("NFC", text).upper()
