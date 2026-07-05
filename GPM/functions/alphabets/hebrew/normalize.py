"""Hebrew Normalisierung — NFC, Niqqud entfernen, Finalformen."""

from __future__ import annotations

import unicodedata

from alphabets.hebrew.map import _FINAL_FORMS


def normalize_hebrew(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    result: list[str] = []
    for ch in text:
        if unicodedata.category(ch).startswith("M"):
            continue
        result.append(_FINAL_FORMS.get(ch, ch))
    return "".join(result)
