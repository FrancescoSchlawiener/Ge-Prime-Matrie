"""Arabic alphabet — 28 Buchstaben, eigener Primblock ab 443."""

from __future__ import annotations

from typing import Final

from alphabets.arabic.frequency import ARABIC_FREQUENCY_DESC
from alphabets.cyrillic.map import CYRILLIC_LAST_PRIME
from alphabets.lex import build_lex_order
from alphabets.primes import last_prime_in_block, next_prime_block

_ARABIC_SYMBOLS: Final[tuple[str, ...]] = (
    "ا", "ب", "ت", "ث", "ج", "ح", "خ", "د", "ذ", "ر", "ز", "س", "ش", "ص",
    "ض", "ط", "ظ", "ع", "غ", "ف", "ق", "ك", "ل", "م", "ن", "ه", "و", "ي",
)

_ARABIC_PRIMES: Final[tuple[int, ...]] = next_prime_block(
    len(_ARABIC_SYMBOLS), after=CYRILLIC_LAST_PRIME
)
ARABIC_LAST_PRIME: Final[int] = last_prime_in_block(_ARABIC_PRIMES)

ALPHA_ARABIC: Final[dict[str, int]] = dict(zip(_ARABIC_SYMBOLS, _ARABIC_PRIMES))
CHAR_ARABIC: Final[dict[int, str]] = {v: k for k, v in ALPHA_ARABIC.items()}
ALPHA_ARABIC_LEX_ORDER: Final[tuple[str, ...]] = build_lex_order(
    _ARABIC_SYMBOLS, ARABIC_FREQUENCY_DESC
)
CHAR_ARABIC_SET: Final[frozenset[str]] = frozenset(ALPHA_ARABIC.keys())
