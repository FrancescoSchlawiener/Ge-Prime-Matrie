"""Old Persian — 36 Keilschrift-Zeichen (SMP U+103A0–U+103C3)."""

from __future__ import annotations

from typing import Final

from alphabets.javanese.map import JAVANESE_LAST_PRIME
from alphabets.lex import build_lex_order
from alphabets.old_persian.frequency import OLD_PERSIAN_FREQUENCY_DESC
from alphabets.primes import last_prime_in_block, next_prime_block

_OLD_PERSIAN_SYMBOLS: Final[tuple[str, ...]] = tuple(
    chr(0x103A0 + i) for i in range(36)
)

_OLD_PERSIAN_PRIMES: Final[tuple[int, ...]] = next_prime_block(
    len(_OLD_PERSIAN_SYMBOLS), after=JAVANESE_LAST_PRIME
)
OLD_PERSIAN_LAST_PRIME: Final[int] = last_prime_in_block(_OLD_PERSIAN_PRIMES)

ALPHA_OLD_PERSIAN: Final[dict[str, int]] = dict(
    zip(_OLD_PERSIAN_SYMBOLS, _OLD_PERSIAN_PRIMES)
)
CHAR_OLD_PERSIAN: Final[dict[int, str]] = {v: k for k, v in ALPHA_OLD_PERSIAN.items()}
ALPHA_OLD_PERSIAN_LEX_ORDER: Final[tuple[str, ...]] = build_lex_order(
    _OLD_PERSIAN_SYMBOLS, OLD_PERSIAN_FREQUENCY_DESC
)
CHAR_OLD_PERSIAN_SET: Final[frozenset[str]] = frozenset(ALPHA_OLD_PERSIAN.keys())
