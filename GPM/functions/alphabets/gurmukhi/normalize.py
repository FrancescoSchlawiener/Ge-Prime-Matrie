"""Gurmukhi Normalisierung — NFC, Matra-Map, Mn-Strip, Whitelist."""

from __future__ import annotations

import unicodedata

from alphabets.gurmukhi.map import CHAR_GURMUKHI_SET

# Matras, Bindi, unabhängige Vokale — explizit verworfen vor Mn-Strip
_MATRA_AND_MARKS: frozenset[str] = frozenset({
    "\u0A3E", "\u0A3F", "\u0A40", "\u0A41", "\u0A42", "\u0A47", "\u0A48",
    "\u0A4B", "\u0A4C", "\u0A4D",
    "\u0A02", "\u0A70", "\u0A71",
    "\u0A05", "\u0A06", "\u0A07", "\u0A08", "\u0A09", "\u0A0A",
    "\u0A0F", "\u0A10", "\u0A13", "\u0A14",
})


def normalize_gurmukhi(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    result: list[str] = []
    for ch in text:
        if ch in _MATRA_AND_MARKS:
            continue
        if unicodedata.category(ch) == "Mn":
            continue
        if ch in CHAR_GURMUKHI_SET:
            result.append(ch)
    return "".join(result)
