"""Devanagari Normalisierung — NFC, virama-stabil."""

from __future__ import annotations

import unicodedata

_VIRAMA = "\u094D"


def normalize_devanagari(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    return text.replace(_VIRAMA, "")
