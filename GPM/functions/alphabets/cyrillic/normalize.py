"""Cyrillic Normalisierung — NFC + Uppercase."""

from __future__ import annotations

import unicodedata


def normalize_cyrillic(text: str) -> str:
    return unicodedata.normalize("NFC", text).upper()
