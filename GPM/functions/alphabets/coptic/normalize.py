"""Coptic Normalisierung — NFC + uppercase."""

from __future__ import annotations

import unicodedata

from alphabets.coptic.map import CHAR_COPTIC_SET


def normalize_coptic(text: str) -> str:
    text = unicodedata.normalize("NFC", text).upper()
    return "".join(ch for ch in text if ch in CHAR_COPTIC_SET)
