"""Phoenician — 22 Konsonanten (SMP U+10900–U+10915)."""

from __future__ import annotations

from typing import Final

from alphabets.lex import build_lex_order
from alphabets.phoenician.frequency import PHOENICIAN_FREQUENCY_DESC
from alphabets.primes import last_prime_in_block, next_prime_block
from alphabets.runic.map import RUNIC_LAST_PRIME

_PHOENICIAN_SYMBOLS: Final[tuple[str, ...]] = tuple(
    chr(0x10900 + i) for i in range(22)
)

_PHOENICIAN_PRIMES: Final[tuple[int, ...]] = next_prime_block(
    len(_PHOENICIAN_SYMBOLS), after=RUNIC_LAST_PRIME
)
PHOENICIAN_LAST_PRIME: Final[int] = last_prime_in_block(_PHOENICIAN_PRIMES)

ALPHA_PHOENICIAN: Final[dict[str, int]] = dict(
    zip(_PHOENICIAN_SYMBOLS, _PHOENICIAN_PRIMES)
)
CHAR_PHOENICIAN: Final[dict[int, str]] = {v: k for k, v in ALPHA_PHOENICIAN.items()}
ALPHA_PHOENICIAN_LEX_ORDER: Final[tuple[str, ...]] = build_lex_order(
    _PHOENICIAN_SYMBOLS, PHOENICIAN_FREQUENCY_DESC
)
CHAR_PHOENICIAN_SET: Final[frozenset[str]] = frozenset(ALPHA_PHOENICIAN.keys())
