"""Roman/Latin — aktiver GPM-Zeichensatz (abgeleitet von OG)."""

from __future__ import annotations

from typing import Final

from alphabets.lex import build_lex_order
from alphabets.og.map import ALPHA_OG, CHAR_OG
from alphabets.roman.frequency import ROMAN_FREQUENCY_DESC

ALPHA_ROMAN: Final[dict[str, int]] = dict(ALPHA_OG)
PRIME_TO_CHAR_ROMAN: Final[dict[int, str]] = {v: k for k, v in ALPHA_ROMAN.items()}
CHAR_ROMAN: Final[frozenset[str]] = frozenset(ALPHA_ROMAN.keys())
ALPHA_ROMAN_LEX_ORDER: Final[tuple[str, ...]] = build_lex_order(
    ALPHA_ROMAN.keys(), ROMAN_FREQUENCY_DESC
)


def is_roman_symbol(char: str) -> bool:
    return char in CHAR_ROMAN


def uses_roman_alpha(normalized: str) -> bool:
    return len(normalized) >= 1 and all(ch in CHAR_ROMAN for ch in normalized)
