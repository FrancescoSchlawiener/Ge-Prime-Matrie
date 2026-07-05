"""Tamil Normalisierung — NFC, Matra/Pulli-Map, Mn-Strip, Whitelist."""

from __future__ import annotations

import unicodedata

from alphabets.tamil.map import CHAR_TAMIL_SET

# Matras → unabhängiges Vokalzeichen aus dem 30er-Satz
_MATRA_TO_VOWEL: dict[str, str] = {
    "\u0BBE": "ஆ",  # aa
    "\u0BBF": "இ",  # i
    "\u0BC0": "ஈ",  # ii
    "\u0BC1": "உ",  # u
    "\u0BC2": "ஊ",  # uu
    "\u0BC6": "எ",  # e
    "\u0BC7": "ஏ",  # ee
    "\u0BC8": "ஐ",  # ai
    "\u0BCA": "ஒ",  # o (combined start)
    "\u0BCB": "ஓ",  # oo
    "\u0BCC": "ஔ",  # au
    "\u0BD7": "ஔ",  # au alt
}

# Pulli, Anusvara, Visarga, kombinatorische Zeichen — verworfen
_EXPLICIT_MARKS: frozenset[str] = frozenset({
    "\u0BCD",  # pulli (virama)
    "\u0B82",  # anusvara
    "\u0B83",  # visarga
    * _MATRA_TO_VOWEL.keys(),
})


def normalize_tamil(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    result: list[str] = []
    for ch in text:
        if ch in _MATRA_TO_VOWEL:
            vowel = _MATRA_TO_VOWEL[ch]
            if vowel in CHAR_TAMIL_SET:
                result.append(vowel)
            continue
        if ch in _EXPLICIT_MARKS:
            continue
        if unicodedata.category(ch) == "Mn":
            continue
        if ch in CHAR_TAMIL_SET:
            result.append(ch)
    return "".join(result)
