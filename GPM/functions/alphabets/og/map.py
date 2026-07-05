"""OG-Alpha-Satz — frozen Referenz (Ge-Prime-Matrix OG PRIME_MAP)."""

from __future__ import annotations

from typing import Final

ALPHA_OG: Final[dict[str, int]] = {
    "A": 3,
    "B": 59,
    "C": 29,
    "D": 31,
    "E": 2,
    "F": 61,
    "G": 53,
    "H": 47,
    "I": 7,
    "J": 97,
    "K": 73,
    "L": 23,
    "M": 41,
    "N": 13,
    "O": 5,
    "P": 43,
    "Q": 101,
    "R": 17,
    "S": 19,
    "T": 11,
    "U": 37,
    "V": 79,
    "W": 71,
    "X": 83,
    "Y": 67,
    "Z": 89,
    "ß": 103,
}

CHAR_OG: Final[dict[int, str]] = {v: k for k, v in ALPHA_OG.items()}
ALPHA_OG_LEX_ORDER: Final[tuple[str, ...]] = tuple(sorted(ALPHA_OG.keys()))
ALPHA_OG_SINGLETON_LUT: Final[tuple[str, ...]] = ALPHA_OG_LEX_ORDER


def is_og_symbol(char: str) -> bool:
    return char in ALPHA_OG


def prime_for_og_symbol(char: str) -> int:
    return ALPHA_OG[char]
