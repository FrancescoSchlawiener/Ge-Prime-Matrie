"""Amharic Normalisierung — NFKD, Silbe→Basis, Whitelist."""

from __future__ import annotations

import unicodedata

from alphabets.amharic.map import CHAR_AMHARIC_SET, _SYLLABLE_TO_BASE


def normalize_amharic(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    result: list[str] = []
    for ch in text:
        if unicodedata.category(ch) == "Mn":
            continue
        if ch in CHAR_AMHARIC_SET:
            result.append(ch)
            continue
        base = _SYLLABLE_TO_BASE.get(ch)
        if base is not None and base in CHAR_AMHARIC_SET:
            result.append(base)
    return "".join(result)
