"""Old Italic — 26 Buchstaben (SMP U+10300–U+10319)."""

from __future__ import annotations

from typing import Final

from alphabets.aesthetic_hieroglyphs.map import AESTHETIC_HIEROGLYPHS_LAST_PRIME
from alphabets.lex import build_lex_order
from alphabets.old_italic.frequency import OLD_ITALIC_FREQUENCY_DESC
from alphabets.primes import last_prime_in_block, next_prime_block

_OLD_ITALIC_SYMBOLS: Final[tuple[str, ...]] = tuple(
    chr(0x10300 + i) for i in range(26)
)

_OLD_ITALIC_PRIMES: Final[tuple[int, ...]] = next_prime_block(
    len(_OLD_ITALIC_SYMBOLS), after=AESTHETIC_HIEROGLYPHS_LAST_PRIME
)
OLD_ITALIC_LAST_PRIME: Final[int] = last_prime_in_block(_OLD_ITALIC_PRIMES)

ALPHA_OLD_ITALIC: Final[dict[str, int]] = dict(
    zip(_OLD_ITALIC_SYMBOLS, _OLD_ITALIC_PRIMES)
)
CHAR_OLD_ITALIC: Final[dict[int, str]] = {v: k for k, v in ALPHA_OLD_ITALIC.items()}
ALPHA_OLD_ITALIC_LEX_ORDER: Final[tuple[str, ...]] = build_lex_order(
    _OLD_ITALIC_SYMBOLS, OLD_ITALIC_FREQUENCY_DESC
)
CHAR_OLD_ITALIC_SET: Final[frozenset[str]] = frozenset(ALPHA_OLD_ITALIC.keys())
