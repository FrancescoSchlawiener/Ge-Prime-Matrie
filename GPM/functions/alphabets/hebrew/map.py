"""Hebrew alphabet — 22 Konsonanten."""

from __future__ import annotations

from typing import Final

from alphabets.arabic.map import ARABIC_LAST_PRIME
from alphabets.hebrew.frequency import HEBREW_FREQUENCY_DESC
from alphabets.lex import build_lex_order
from alphabets.primes import last_prime_in_block, next_prime_block

_HEBREW_SYMBOLS: Final[tuple[str, ...]] = (
    "א", "ב", "ג", "ד", "ה", "ו", "ז", "ח", "ט", "י", "כ", "ל", "מ", "נ",
    "ס", "ע", "פ", "צ", "ק", "ר", "ש", "ת",
)

_HEBREW_PRIMES: Final[tuple[int, ...]] = next_prime_block(
    len(_HEBREW_SYMBOLS), after=ARABIC_LAST_PRIME
)
HEBREW_LAST_PRIME: Final[int] = last_prime_in_block(_HEBREW_PRIMES)

ALPHA_HEBREW: Final[dict[str, int]] = dict(zip(_HEBREW_SYMBOLS, _HEBREW_PRIMES))
CHAR_HEBREW: Final[dict[int, str]] = {v: k for k, v in ALPHA_HEBREW.items()}
ALPHA_HEBREW_LEX_ORDER: Final[tuple[str, ...]] = build_lex_order(
    _HEBREW_SYMBOLS, HEBREW_FREQUENCY_DESC
)
CHAR_HEBREW_SET: Final[frozenset[str]] = frozenset(ALPHA_HEBREW.keys())

_FINAL_FORMS: Final[dict[str, str]] = {"ך": "כ", "ם": "מ", "ן": "נ", "ף": "פ", "ץ": "צ"}
