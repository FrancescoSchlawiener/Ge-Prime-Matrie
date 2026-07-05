"""Thaana — 24 Buchstaben (U+0780–U+0797)."""

from __future__ import annotations

from typing import Final

from alphabets.lex import build_lex_order
from alphabets.mongolian.map import MONGOLIAN_LAST_PRIME
from alphabets.primes import last_prime_in_block, next_prime_block
from alphabets.thaana.frequency import THAANA_FREQUENCY_DESC

_THAANA_SYMBOLS: Final[tuple[str, ...]] = tuple(
    chr(0x0780 + i) for i in range(24)
)

_THAANA_PRIMES: Final[tuple[int, ...]] = next_prime_block(
    len(_THAANA_SYMBOLS), after=MONGOLIAN_LAST_PRIME
)
THAANA_LAST_PRIME: Final[int] = last_prime_in_block(_THAANA_PRIMES)

ALPHA_THAANA: Final[dict[str, int]] = dict(zip(_THAANA_SYMBOLS, _THAANA_PRIMES))
CHAR_THAANA: Final[dict[int, str]] = {v: k for k, v in ALPHA_THAANA.items()}
ALPHA_THAANA_LEX_ORDER: Final[tuple[str, ...]] = build_lex_order(
    _THAANA_SYMBOLS, THAANA_FREQUENCY_DESC
)
CHAR_THAANA_SET: Final[frozenset[str]] = frozenset(ALPHA_THAANA.keys())
