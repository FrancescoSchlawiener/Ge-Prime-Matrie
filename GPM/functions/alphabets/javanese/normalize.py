"""Javanese Normalisierung — Pasangan/Diakritika-Strip, Hanacaraka-Whitelist."""

from __future__ import annotations

import unicodedata

from alphabets.javanese.map import CHAR_JAVANESE_SET

_SKIP: frozenset[str] = frozenset({
    "\uA9BC", "\uA9BD", "\uA9BE", "\uA9BF", "\uA9C0",
})
_WYANJANA: frozenset[str] = frozenset(chr(cp) for cp in range(0xA9B4, 0xA9BC))


def normalize_javanese(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    result: list[str] = []
    for ch in text:
        if ch in _SKIP or ch in _WYANJANA:
            continue
        if unicodedata.category(ch) in ("Mn", "Mc"):
            continue
        if ch in CHAR_JAVANESE_SET:
            result.append(ch)
    return "".join(result)
