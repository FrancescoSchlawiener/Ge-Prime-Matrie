"""Greek alphabet — eigener Primblock."""

from __future__ import annotations

from typing import Final

_GREEK_SYMBOLS: Final[tuple[str, ...]] = (
    "Α", "Β", "Γ", "Δ", "Ε", "Ζ", "Η", "Θ", "Ι", "Κ", "Λ", "Μ",
    "Ν", "Ξ", "Ο", "Π", "Ρ", "Σ", "Τ", "Υ", "Φ", "Χ", "Ψ", "Ω",
)

# Primzahlen ab 109 (nach OG ß=103)
_GREEK_PRIMES: Final[tuple[int, ...]] = (
    109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173,
    179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239,
)

ALPHA_GREEK: Final[dict[str, int]] = dict(zip(_GREEK_SYMBOLS, _GREEK_PRIMES))
CHAR_GREEK: Final[dict[int, str]] = {v: k for k, v in ALPHA_GREEK.items()}
ALPHA_GREEK_LEX_ORDER: Final[tuple[str, ...]] = _GREEK_SYMBOLS
CHAR_GREEK_SET: Final[frozenset[str]] = frozenset(ALPHA_GREEK.keys())
