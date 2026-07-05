"""Aesthetic Hieroglyphs — 24 Uniliterale (Gardiner-Phonem-Set)."""

from __future__ import annotations

from typing import Final

from alphabets.aesthetic_hieroglyphs.frequency import (
    AESTHETIC_HIEROGLYPHS_FREQUENCY_DESC,
    _UNI,
)
from alphabets.lex import build_lex_order
from alphabets.old_persian.map import OLD_PERSIAN_LAST_PRIME
from alphabets.primes import last_prime_in_block, next_prime_block

_AESTHETIC_HIEROGLYPHS_SYMBOLS: Final[tuple[str, ...]] = _UNI

_AESTHETIC_HIEROGLYPHS_PRIMES: Final[tuple[int, ...]] = next_prime_block(
    len(_AESTHETIC_HIEROGLYPHS_SYMBOLS), after=OLD_PERSIAN_LAST_PRIME
)
AESTHETIC_HIEROGLYPHS_LAST_PRIME: Final[int] = last_prime_in_block(
    _AESTHETIC_HIEROGLYPHS_PRIMES
)

ALPHA_AESTHETIC_HIEROGLYPHS: Final[dict[str, int]] = dict(
    zip(_AESTHETIC_HIEROGLYPHS_SYMBOLS, _AESTHETIC_HIEROGLYPHS_PRIMES)
)
CHAR_AESTHETIC_HIEROGLYPHS: Final[dict[int, str]] = {
    v: k for k, v in ALPHA_AESTHETIC_HIEROGLYPHS.items()
}
ALPHA_AESTHETIC_HIEROGLYPHS_LEX_ORDER: Final[tuple[str, ...]] = build_lex_order(
    _AESTHETIC_HIEROGLYPHS_SYMBOLS, AESTHETIC_HIEROGLYPHS_FREQUENCY_DESC
)
CHAR_AESTHETIC_HIEROGLYPHS_SET: Final[frozenset[str]] = frozenset(
    ALPHA_AESTHETIC_HIEROGLYPHS.keys()
)
