"""Javanese — 20 Hanacaraka-Kern-Aksara (U+A992–U+A9A5)."""

from __future__ import annotations

from typing import Final

from alphabets.javanese.frequency import JAVANESE_FREQUENCY_DESC
from alphabets.lex import build_lex_order
from alphabets.primes import last_prime_in_block, next_prime_block
from alphabets.telugu.map import TELUGU_LAST_PRIME

_JAVANESE_SYMBOLS: Final[tuple[str, ...]] = tuple(
    chr(0xA992 + i) for i in range(20)
)

_JAVANESE_PRIMES: Final[tuple[int, ...]] = next_prime_block(
    len(_JAVANESE_SYMBOLS), after=TELUGU_LAST_PRIME
)
JAVANESE_LAST_PRIME: Final[int] = last_prime_in_block(_JAVANESE_PRIMES)

ALPHA_JAVANESE: Final[dict[str, int]] = dict(
    zip(_JAVANESE_SYMBOLS, _JAVANESE_PRIMES)
)
CHAR_JAVANESE: Final[dict[int, str]] = {v: k for k, v in ALPHA_JAVANESE.items()}
ALPHA_JAVANESE_LEX_ORDER: Final[tuple[str, ...]] = build_lex_order(
    _JAVANESE_SYMBOLS, JAVANESE_FREQUENCY_DESC
)
CHAR_JAVANESE_SET: Final[frozenset[str]] = frozenset(ALPHA_JAVANESE.keys())
