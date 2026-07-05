"""Mongolian — 35 Basis-Grapheme (isolierte Form U+1820–U+1842)."""

from __future__ import annotations

from typing import Final

from alphabets.gothic.map import GOTHIC_LAST_PRIME
from alphabets.lex import build_lex_order
from alphabets.mongolian.frequency import MONGOLIAN_FREQUENCY_DESC
from alphabets.primes import last_prime_in_block, next_prime_block

_MONGOLIAN_SYMBOLS: Final[tuple[str, ...]] = tuple(
    chr(0x1820 + i) for i in range(35)
)

_MONGOLIAN_PRIMES: Final[tuple[int, ...]] = next_prime_block(
    len(_MONGOLIAN_SYMBOLS), after=GOTHIC_LAST_PRIME
)
MONGOLIAN_LAST_PRIME: Final[int] = last_prime_in_block(_MONGOLIAN_PRIMES)

ALPHA_MONGOLIAN: Final[dict[str, int]] = dict(
    zip(_MONGOLIAN_SYMBOLS, _MONGOLIAN_PRIMES)
)
CHAR_MONGOLIAN: Final[dict[int, str]] = {v: k for k, v in ALPHA_MONGOLIAN.items()}
ALPHA_MONGOLIAN_LEX_ORDER: Final[tuple[str, ...]] = build_lex_order(
    _MONGOLIAN_SYMBOLS, MONGOLIAN_FREQUENCY_DESC
)
CHAR_MONGOLIAN_SET: Final[frozenset[str]] = frozenset(ALPHA_MONGOLIAN.keys())
