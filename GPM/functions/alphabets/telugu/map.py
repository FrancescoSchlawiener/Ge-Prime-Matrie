"""Telugu — 35 Basis-Konsonanten."""

from __future__ import annotations

from typing import Final

from alphabets.bengali.map import BENGALI_LAST_PRIME
from alphabets.lex import build_lex_order
from alphabets.primes import last_prime_in_block, next_prime_block
from alphabets.telugu.frequency import TELUGU_FREQUENCY_DESC

_TELUGU_SYMBOLS: Final[tuple[str, ...]] = (
    "క", "ఖ", "గ", "ఘ", "ఙ", "చ", "ఛ", "జ", "ఝ", "ఞ", "ట", "ఠ", "డ", "ఢ", "ణ",
    "త", "థ", "ద", "ధ", "న", "ప", "ఫ", "బ", "భ", "మ", "య", "ర", "ఱ", "ల", "ళ",
    "వ", "శ", "ష", "స", "హ",
)

_TELUGU_PRIMES: Final[tuple[int, ...]] = next_prime_block(
    len(_TELUGU_SYMBOLS), after=BENGALI_LAST_PRIME
)
TELUGU_LAST_PRIME: Final[int] = last_prime_in_block(_TELUGU_PRIMES)

ALPHA_TELUGU: Final[dict[str, int]] = dict(zip(_TELUGU_SYMBOLS, _TELUGU_PRIMES))
CHAR_TELUGU: Final[dict[int, str]] = {v: k for k, v in ALPHA_TELUGU.items()}
ALPHA_TELUGU_LEX_ORDER: Final[tuple[str, ...]] = build_lex_order(
    _TELUGU_SYMBOLS, TELUGU_FREQUENCY_DESC
)
CHAR_TELUGU_SET: Final[frozenset[str]] = frozenset(ALPHA_TELUGU.keys())
