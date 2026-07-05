"""Bengali Normalisierung — NFC, Matra-Strip, Mn-Strip, Whitelist."""

from __future__ import annotations

import unicodedata

from alphabets.bengali.map import CHAR_BENGALI_SET

_MATRA_AND_MARKS: frozenset[str] = frozenset({
    "\u09BE", "\u09BF", "\u09C0", "\u09C1", "\u09C2", "\u09C3", "\u09C4",
    "\u09C7", "\u09C8", "\u09CB", "\u09CC", "\u09CD", "\u09D7",
    "\u0981", "\u0982", "\u0983",
    "\u0985", "\u0986", "\u0987", "\u0988", "\u0989", "\u098A", "\u098B", "\u098C",
    "\u098F", "\u0990", "\u0993", "\u0994",
})


def normalize_bengali(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    result: list[str] = []
    for ch in text:
        if ch in _MATRA_AND_MARKS:
            continue
        if unicodedata.category(ch) == "Mn":
            continue
        if ch in CHAR_BENGALI_SET:
            result.append(ch)
    return "".join(result)
