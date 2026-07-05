"""Latin/Roman Normalisierung — eszett-aware, Umlaute."""

from __future__ import annotations

import unicodedata

from alphabets.profiles import AlphabetProfile
from alphabets.roman.map import CHAR_ROMAN, prime_map_for_profile

_UMLAUT_MAP: dict[str, str] = {
    "ä": "ae", "ö": "oe", "ü": "ue",
    "Ä": "AE", "Ö": "OE", "Ü": "UE",
}


def _eszett_aware_upper(text: str) -> str:
    return "".join(ch if ch == "ß" else ch.upper() for ch in text)


def normalize_latin(word: str) -> str:
    word = unicodedata.normalize("NFC", word)
    for src, dst in _UMLAUT_MAP.items():
        word = word.replace(src, dst)
    word = word.replace("ẞ", "ß")
    return _eszett_aware_upper(word)


def prepare_substrate(raw: str, profile: AlphabetProfile | str = AlphabetProfile.ROMAN) -> str:
    text = unicodedata.normalize("NFC", (raw or "").strip())
    if profile in (AlphabetProfile.GREEK, "greek"):
        from alphabets.greek.normalize import normalize_greek
        return normalize_greek(text)
    if profile in (AlphabetProfile.CYRILLIC, "cyrillic"):
        from alphabets.cyrillic.normalize import normalize_cyrillic
        return normalize_cyrillic(text)
    return normalize_latin(text)


def is_valid_substrate(text: str, profile: AlphabetProfile | str = AlphabetProfile.ROMAN) -> bool:
    if len(text) < 1:
        return False
    if profile in (AlphabetProfile.ROMAN, "roman"):
        return all(ch in CHAR_ROMAN for ch in text)
    prime_map = prime_map_for_profile(profile)
    return all(ch in prime_map for ch in text)


def is_valid_roman_substrate(text: str) -> bool:
    return len(text) >= 1 and all(ch in CHAR_ROMAN for ch in text)


def is_valid_og_substrate(text: str) -> bool:
    return is_valid_substrate(text, AlphabetProfile.OG)


normalize_word = prepare_substrate
is_valid_normalized = is_valid_og_substrate
