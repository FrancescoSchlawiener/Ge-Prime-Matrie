"""Old Turkic — 38 Orkhon-Runen (SMP U+10C00–U+10C25)."""

from __future__ import annotations

from typing import Final

from alphabets.lex import build_lex_order
from alphabets.old_italic.map import OLD_ITALIC_LAST_PRIME
from alphabets.old_turkic.frequency import OLD_TURKIC_FREQUENCY_DESC
from alphabets.primes import last_prime_in_block, next_prime_block

_OLD_TURKIC_SYMBOLS: Final[tuple[str, ...]] = tuple(
    chr(0x10C00 + i) for i in range(38)
)

_OLD_TURKIC_PRIMES: Final[tuple[int, ...]] = next_prime_block(
    len(_OLD_TURKIC_SYMBOLS), after=OLD_ITALIC_LAST_PRIME
)
OLD_TURKIC_LAST_PRIME: Final[int] = last_prime_in_block(_OLD_TURKIC_PRIMES)

ALPHA_OLD_TURKIC: Final[dict[str, int]] = dict(
    zip(_OLD_TURKIC_SYMBOLS, _OLD_TURKIC_PRIMES)
)
CHAR_OLD_TURKIC: Final[dict[int, str]] = {v: k for k, v in ALPHA_OLD_TURKIC.items()}
ALPHA_OLD_TURKIC_LEX_ORDER: Final[tuple[str, ...]] = build_lex_order(
    _OLD_TURKIC_SYMBOLS, OLD_TURKIC_FREQUENCY_DESC
)
CHAR_OLD_TURKIC_SET: Final[frozenset[str]] = frozenset(ALPHA_OLD_TURKIC.keys())
