"""Ugaritic — 30 Keilschrift-Zeichen (SMP U+10380–U+1039D)."""

from __future__ import annotations

from typing import Final

from alphabets.lex import build_lex_order
from alphabets.phoenician.map import PHOENICIAN_LAST_PRIME
from alphabets.primes import last_prime_in_block, next_prime_block
from alphabets.ugaritic.frequency import UGARITIC_FREQUENCY_DESC

_UGARITIC_SYMBOLS: Final[tuple[str, ...]] = tuple(
    chr(0x10380 + i) for i in range(30)
)

_UGARITIC_PRIMES: Final[tuple[int, ...]] = next_prime_block(
    len(_UGARITIC_SYMBOLS), after=PHOENICIAN_LAST_PRIME
)
UGARITIC_LAST_PRIME: Final[int] = last_prime_in_block(_UGARITIC_PRIMES)

ALPHA_UGARITIC: Final[dict[str, int]] = dict(
    zip(_UGARITIC_SYMBOLS, _UGARITIC_PRIMES)
)
CHAR_UGARITIC: Final[dict[int, str]] = {v: k for k, v in ALPHA_UGARITIC.items()}
ALPHA_UGARITIC_LEX_ORDER: Final[tuple[str, ...]] = build_lex_order(
    _UGARITIC_SYMBOLS, UGARITIC_FREQUENCY_DESC
)
CHAR_UGARITIC_SET: Final[frozenset[str]] = frozenset(ALPHA_UGARITIC.keys())
