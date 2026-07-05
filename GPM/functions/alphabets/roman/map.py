"""Roman/Latin — aktiver GPM-Zeichensatz (abgeleitet von OG)."""

from __future__ import annotations

from typing import Final

from alphabets.greek.map import ALPHA_GREEK, CHAR_GREEK
from alphabets.cyrillic.map import ALPHA_CYRILLIC, CHAR_CYRILLIC
from alphabets.og.map import ALPHA_OG, CHAR_OG
from alphabets.profiles import AlphabetProfile

ALPHA_ROMAN: Final[dict[str, int]] = dict(ALPHA_OG)
PRIME_TO_CHAR_ROMAN: Final[dict[int, str]] = {v: k for k, v in ALPHA_ROMAN.items()}
CHAR_ROMAN: Final[frozenset[str]] = frozenset(ALPHA_ROMAN.keys())
ALPHA_ROMAN_LEX_ORDER: Final[tuple[str, ...]] = tuple(sorted(ALPHA_ROMAN.keys()))


def is_roman_symbol(char: str) -> bool:
    return char in CHAR_ROMAN


def uses_roman_alpha(normalized: str) -> bool:
    return len(normalized) >= 1 and all(ch in CHAR_ROMAN for ch in normalized)


def prime_map_for_profile(profile: AlphabetProfile | str) -> dict[str, int]:
    if isinstance(profile, str):
        profile = AlphabetProfile(profile)
    if profile is AlphabetProfile.OG:
        return ALPHA_OG
    if profile is AlphabetProfile.ROMAN:
        return ALPHA_ROMAN
    if profile is AlphabetProfile.GREEK:
        return ALPHA_GREEK
    if profile is AlphabetProfile.CYRILLIC:
        return ALPHA_CYRILLIC
    raise ValueError(f"Unbekanntes AlphabetProfile: {profile!r}")


def char_map_for_profile(profile: AlphabetProfile | str) -> dict[int, str]:
    if isinstance(profile, str):
        profile = AlphabetProfile(profile)
    if profile is AlphabetProfile.OG:
        return CHAR_OG
    if profile is AlphabetProfile.ROMAN:
        return PRIME_TO_CHAR_ROMAN
    if profile is AlphabetProfile.GREEK:
        return CHAR_GREEK
    if profile is AlphabetProfile.CYRILLIC:
        return CHAR_CYRILLIC
    raise ValueError(f"Unbekanntes AlphabetProfile: {profile!r}")
