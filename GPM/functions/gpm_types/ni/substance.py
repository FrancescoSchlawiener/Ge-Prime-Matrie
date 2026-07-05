"""N(I) Substanz — Primprodukt über Ziffern."""

from __future__ import annotations

from gpm_types.ni.canonical import canonical_n

# Ziffern 0–9 → Primzahlen (eigener Block, getrennt von Buchstaben-Alpha)
DIGIT_PRIMES: dict[str, int] = {
    "0": 2,
    "1": 3,
    "2": 5,
    "3": 7,
    "4": 11,
    "5": 13,
    "6": 17,
    "7": 19,
    "8": 23,
    "9": 29,
}


def substance_n(raw: str) -> int:
    canon = canonical_n(raw)
    s = 1
    for ch in canon:
        s *= DIGIT_PRIMES[ch]
    return s
