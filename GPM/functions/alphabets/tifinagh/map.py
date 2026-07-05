"""Tifinagh — 33 IRCAM Neo-Tifinagh Zeichen."""

from __future__ import annotations

from typing import Final

from alphabets.lex import build_lex_order
from alphabets.primes import last_prime_in_block, next_prime_block
from alphabets.thaana.map import THAANA_LAST_PRIME
from alphabets.tifinagh.frequency import _TIFINAGH_IRCAM, TIFINAGH_FREQUENCY_DESC

_TIFINAGH_SYMBOLS: Final[tuple[str, ...]] = tuple(_TIFINAGH_IRCAM)

_TIFINAGH_PRIMES: Final[tuple[int, ...]] = next_prime_block(
    len(_TIFINAGH_SYMBOLS), after=THAANA_LAST_PRIME
)
TIFINAGH_LAST_PRIME: Final[int] = last_prime_in_block(_TIFINAGH_PRIMES)

ALPHA_TIFINAGH: Final[dict[str, int]] = dict(
    zip(_TIFINAGH_SYMBOLS, _TIFINAGH_PRIMES)
)
CHAR_TIFINAGH: Final[dict[int, str]] = {v: k for k, v in ALPHA_TIFINAGH.items()}
ALPHA_TIFINAGH_LEX_ORDER: Final[tuple[str, ...]] = build_lex_order(
    _TIFINAGH_SYMBOLS, TIFINAGH_FREQUENCY_DESC
)
CHAR_TIFINAGH_SET: Final[frozenset[str]] = frozenset(ALPHA_TIFINAGH.keys())
