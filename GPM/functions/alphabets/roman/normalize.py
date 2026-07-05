"""Latin/Roman Normalisierung — Shim → alphabets.normalize."""

from __future__ import annotations

from alphabets.normalize import (
    is_valid_substrate,
    normalize_latin,
    prepare_substrate,
)
from alphabets.profiles import AlphabetProfile
from alphabets.roman.map import CHAR_ROMAN


def is_valid_roman_substrate(text: str) -> bool:
    return len(text) >= 1 and all(ch in CHAR_ROMAN for ch in text)


def is_valid_og_substrate(text: str) -> bool:
    return is_valid_substrate(text, AlphabetProfile.OG)


normalize_word = prepare_substrate
is_valid_normalized = is_valid_og_substrate

__all__ = [
    "is_valid_og_substrate",
    "is_valid_roman_substrate",
    "is_valid_substrate",
    "normalize_latin",
    "normalize_word",
    "prepare_substrate",
]
