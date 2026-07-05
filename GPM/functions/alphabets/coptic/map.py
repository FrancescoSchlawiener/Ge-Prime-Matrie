"""Coptic — 32 Buchstaben."""

from __future__ import annotations

from typing import Final

from alphabets.amharic.map import AMHARIC_LAST_PRIME
from alphabets.coptic.frequency import COPTIC_FREQUENCY_DESC
from alphabets.lex import build_lex_order
from alphabets.primes import last_prime_in_block, next_prime_block

_COPTIC_SYMBOLS: Final[tuple[str, ...]] = tuple(
    chr(0x2C80 + 2 * i) for i in range(32)
)

_COPTIC_PRIMES: Final[tuple[int, ...]] = next_prime_block(
    len(_COPTIC_SYMBOLS), after=AMHARIC_LAST_PRIME
)
COPTIC_LAST_PRIME: Final[int] = last_prime_in_block(_COPTIC_PRIMES)

ALPHA_COPTIC: Final[dict[str, int]] = dict(zip(_COPTIC_SYMBOLS, _COPTIC_PRIMES))
CHAR_COPTIC: Final[dict[int, str]] = {v: k for k, v in ALPHA_COPTIC.items()}
ALPHA_COPTIC_LEX_ORDER: Final[tuple[str, ...]] = build_lex_order(
    _COPTIC_SYMBOLS, COPTIC_FREQUENCY_DESC
)
CHAR_COPTIC_SET: Final[frozenset[str]] = frozenset(ALPHA_COPTIC.keys())
