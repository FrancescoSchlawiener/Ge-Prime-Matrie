"""Runic — 24 Elder Futhark."""

from __future__ import annotations

from typing import Final

from alphabets.coptic.map import COPTIC_LAST_PRIME
from alphabets.lex import build_lex_order
from alphabets.primes import last_prime_in_block, next_prime_block
from alphabets.runic.frequency import RUNIC_FREQUENCY_DESC

_RUNIC_SYMBOLS: Final[tuple[str, ...]] = (
    "ᚠ", "ᚢ", "ᚦ", "ᚨ", "ᚱ", "ᚲ", "ᚷ", "ᚹ", "ᚺ", "ᚾ", "ᛁ", "ᛃ", "ᛇ", "ᛈ",
    "ᛉ", "ᛊ", "ᛏ", "ᛒ", "ᛖ", "ᛗ", "ᛚ", "ᛜ", "ᛞ", "ᛟ",
)

_RUNIC_PRIMES: Final[tuple[int, ...]] = next_prime_block(
    len(_RUNIC_SYMBOLS), after=COPTIC_LAST_PRIME
)
RUNIC_LAST_PRIME: Final[int] = last_prime_in_block(_RUNIC_PRIMES)

ALPHA_RUNIC: Final[dict[str, int]] = dict(zip(_RUNIC_SYMBOLS, _RUNIC_PRIMES))
CHAR_RUNIC: Final[dict[int, str]] = {v: k for k, v in ALPHA_RUNIC.items()}
ALPHA_RUNIC_LEX_ORDER: Final[tuple[str, ...]] = build_lex_order(
    _RUNIC_SYMBOLS, RUNIC_FREQUENCY_DESC
)
CHAR_RUNIC_SET: Final[frozenset[str]] = frozenset(ALPHA_RUNIC.keys())
