"""Glagolitic — 41 Buchstaben (U+2C00–U+2C28)."""

from __future__ import annotations

from typing import Final

from alphabets.glagolitic.frequency import GLAGOLITIC_FREQUENCY_DESC
from alphabets.lex import build_lex_order
from alphabets.ogham.map import OGHAM_LAST_PRIME
from alphabets.primes import last_prime_in_block, next_prime_block

_GLAGOLITIC_SYMBOLS: Final[tuple[str, ...]] = tuple(
    chr(0x2C00 + i) for i in range(41)
)

_GLAGOLITIC_PRIMES: Final[tuple[int, ...]] = next_prime_block(
    len(_GLAGOLITIC_SYMBOLS), after=OGHAM_LAST_PRIME
)
GLAGOLITIC_LAST_PRIME: Final[int] = last_prime_in_block(_GLAGOLITIC_PRIMES)

ALPHA_GLAGOLITIC: Final[dict[str, int]] = dict(
    zip(_GLAGOLITIC_SYMBOLS, _GLAGOLITIC_PRIMES)
)
CHAR_GLAGOLITIC: Final[dict[int, str]] = {v: k for k, v in ALPHA_GLAGOLITIC.items()}
ALPHA_GLAGOLITIC_LEX_ORDER: Final[tuple[str, ...]] = build_lex_order(
    _GLAGOLITIC_SYMBOLS, GLAGOLITIC_FREQUENCY_DESC
)
CHAR_GLAGOLITIC_SET: Final[frozenset[str]] = frozenset(ALPHA_GLAGOLITIC.keys())
