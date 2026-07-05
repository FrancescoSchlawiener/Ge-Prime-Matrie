"""Hangul — 51 Jamo (19 Choseong + 21 Jungseong + 11 compound Jongseong)."""

from __future__ import annotations

from typing import Final

from alphabets.hangul.frequency import HANGUL_FREQUENCY_DESC
from alphabets.lex import build_lex_order
from alphabets.primes import last_prime_in_block, next_prime_block
from alphabets.thai.map import THAI_LAST_PRIME

# Choseong (19)
_CHOSEONG: Final[tuple[str, ...]] = (
    "ᄀ", "ᄁ", "ᄂ", "ᄃ", "ᄄ", "ᄅ", "ᄆ", "ᄇ", "ᄈ", "ᄉ", "ᄊ", "ᄋ", "ᄌ", "ᄍ",
    "ᄎ", "ᄏ", "ᄐ", "ᄑ", "ᄒ",
)
# Jungseong (21)
_JUNGSEONG: Final[tuple[str, ...]] = (
    "ᅡ", "ᅢ", "ᅣ", "ᅤ", "ᅥ", "ᅦ", "ᅧ", "ᅨ", "ᅩ", "ᅪ", "ᅫ", "ᅬ", "ᅭ", "ᅮ", "ᅯ",
    "ᅰ", "ᅱ", "ᅲ", "ᅳ", "ᅴ", "ᅵ",
)
# Jongseong-only compounds (11, nicht in Choseong)
_JONGSEONG_EXTRA: Final[tuple[str, ...]] = (
    "ᆪ", "ᆬ", "ᆭ", "ᆰ", "ᆱ", "ᆲ", "ᆳ", "ᆴ", "ᆵ", "ᆶ", "ᆹ",
)

_HANGUL_SYMBOLS: Final[tuple[str, ...]] = _CHOSEONG + _JUNGSEONG + _JONGSEONG_EXTRA

_HANGUL_PRIMES: Final[tuple[int, ...]] = next_prime_block(
    len(_HANGUL_SYMBOLS), after=THAI_LAST_PRIME
)
HANGUL_LAST_PRIME: Final[int] = last_prime_in_block(_HANGUL_PRIMES)

ALPHA_HANGUL: Final[dict[str, int]] = dict(zip(_HANGUL_SYMBOLS, _HANGUL_PRIMES))
CHAR_HANGUL: Final[dict[int, str]] = {v: k for k, v in ALPHA_HANGUL.items()}
ALPHA_HANGUL_LEX_ORDER: Final[tuple[str, ...]] = build_lex_order(
    _HANGUL_SYMBOLS, HANGUL_FREQUENCY_DESC
)
CHAR_HANGUL_SET: Final[frozenset[str]] = frozenset(ALPHA_HANGUL.keys())
