"""Ogham — 20 Kern-Buchstaben (Beith–Iod, ohne Forfeda)."""

from __future__ import annotations

from typing import Final

from alphabets.lex import build_lex_order
from alphabets.ogham.frequency import OGHAM_FREQUENCY_DESC
from alphabets.primes import last_prime_in_block, next_prime_block
from alphabets.ugaritic.map import UGARITIC_LAST_PRIME

_OGHAM_SYMBOLS: Final[tuple[str, ...]] = tuple(
    chr(0x1681 + i) for i in range(20)
)

_OGHAM_PRIMES: Final[tuple[int, ...]] = next_prime_block(
    len(_OGHAM_SYMBOLS), after=UGARITIC_LAST_PRIME
)
OGHAM_LAST_PRIME: Final[int] = last_prime_in_block(_OGHAM_PRIMES)

ALPHA_OGHAM: Final[dict[str, int]] = dict(zip(_OGHAM_SYMBOLS, _OGHAM_PRIMES))
CHAR_OGHAM: Final[dict[int, str]] = {v: k for k, v in ALPHA_OGHAM.items()}
ALPHA_OGHAM_LEX_ORDER: Final[tuple[str, ...]] = build_lex_order(
    _OGHAM_SYMBOLS, OGHAM_FREQUENCY_DESC
)
CHAR_OGHAM_SET: Final[frozenset[str]] = frozenset(ALPHA_OGHAM.keys())
