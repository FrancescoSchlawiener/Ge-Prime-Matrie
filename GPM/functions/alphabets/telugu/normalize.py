"""Telugu Normalisierung — NFC, Matra-Strip, Mn-Strip, Whitelist."""

from __future__ import annotations

import unicodedata

from alphabets.telugu.map import CHAR_TELUGU_SET

_MATRA_AND_MARKS: frozenset[str] = frozenset({
    "\u0C3E", "\u0C3F", "\u0C40", "\u0C41", "\u0C42", "\u0C43", "\u0C44",
    "\u0C46", "\u0C47", "\u0C48", "\u0C4A", "\u0C4B", "\u0C4C", "\u0C4D",
    "\u0C02", "\u0C03",
    "\u0C05", "\u0C06", "\u0C07", "\u0C08", "\u0C09", "\u0C0A", "\u0C0B", "\u0C0C",
    "\u0C0E", "\u0C0F", "\u0C10", "\u0C12", "\u0C13", "\u0C14",
})


def normalize_telugu(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    result: list[str] = []
    for ch in text:
        if ch in _MATRA_AND_MARKS:
            continue
        if unicodedata.category(ch) == "Mn":
            continue
        if ch in CHAR_TELUGU_SET:
            result.append(ch)
    return "".join(result)
