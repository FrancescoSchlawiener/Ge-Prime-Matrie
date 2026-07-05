"""Gurmukhi — 35 Basis-Konsonanten."""

from __future__ import annotations

from typing import Final

from alphabets.georgian.map import GEORGIAN_LAST_PRIME
from alphabets.gurmukhi.frequency import GURMUKHI_FREQUENCY_DESC
from alphabets.lex import build_lex_order
from alphabets.primes import last_prime_in_block, next_prime_block

_GURMUKHI_SYMBOLS: Final[tuple[str, ...]] = (
    "ਕ", "ਖ", "ਗ", "ਘ", "ਙ", "ਚ", "ਛ", "ਜ", "ਝ", "ਞ", "ਟ", "ਠ", "ਡ", "ਢ", "ਣ",
    "ਤ", "ਥ", "ਦ", "ਧ", "ਨ", "ਪ", "ਫ", "ਬ", "ਭ", "ਮ", "ਯ", "ਰ", "ਲ", "ਵ", "ੜ",
    "ਸ", "ਹ", "ਖ਼", "ਗ਼", "ਜ਼",
)

_GURMUKHI_PRIMES: Final[tuple[int, ...]] = next_prime_block(
    len(_GURMUKHI_SYMBOLS), after=GEORGIAN_LAST_PRIME
)
GURMUKHI_LAST_PRIME: Final[int] = last_prime_in_block(_GURMUKHI_PRIMES)

ALPHA_GURMUKHI: Final[dict[str, int]] = dict(zip(_GURMUKHI_SYMBOLS, _GURMUKHI_PRIMES))
CHAR_GURMUKHI: Final[dict[int, str]] = {v: k for k, v in ALPHA_GURMUKHI.items()}
ALPHA_GURMUKHI_LEX_ORDER: Final[tuple[str, ...]] = build_lex_order(
    _GURMUKHI_SYMBOLS, GURMUKHI_FREQUENCY_DESC
)
CHAR_GURMUKHI_SET: Final[frozenset[str]] = frozenset(ALPHA_GURMUKHI.keys())
