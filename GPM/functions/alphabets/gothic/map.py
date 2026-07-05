"""Gothic — 27 Buchstaben (SMP U+10330–U+1034A)."""

from __future__ import annotations

from typing import Final

from alphabets.glagolitic.map import GLAGOLITIC_LAST_PRIME
from alphabets.gothic.frequency import GOTHIC_FREQUENCY_DESC
from alphabets.lex import build_lex_order
from alphabets.primes import last_prime_in_block, next_prime_block

_GOTHIC_SYMBOLS: Final[tuple[str, ...]] = tuple(
    chr(0x10330 + i) for i in range(27)
)

_GOTHIC_PRIMES: Final[tuple[int, ...]] = next_prime_block(
    len(_GOTHIC_SYMBOLS), after=GLAGOLITIC_LAST_PRIME
)
GOTHIC_LAST_PRIME: Final[int] = last_prime_in_block(_GOTHIC_PRIMES)

ALPHA_GOTHIC: Final[dict[str, int]] = dict(zip(_GOTHIC_SYMBOLS, _GOTHIC_PRIMES))
CHAR_GOTHIC: Final[dict[int, str]] = {v: k for k, v in ALPHA_GOTHIC.items()}
ALPHA_GOTHIC_LEX_ORDER: Final[tuple[str, ...]] = build_lex_order(
    _GOTHIC_SYMBOLS, GOTHIC_FREQUENCY_DESC
)
CHAR_GOTHIC_SET: Final[frozenset[str]] = frozenset(ALPHA_GOTHIC.keys())
