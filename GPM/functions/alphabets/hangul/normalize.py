"""Hangul Normalisierung — NFKD → Jamo-Zerlegung."""

from __future__ import annotations

import unicodedata

from alphabets.hangul.map import CHAR_HANGUL_SET


def normalize_hangul(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if ch in CHAR_HANGUL_SET)
