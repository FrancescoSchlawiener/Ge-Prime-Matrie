"""C(I) Registry-Identität — C_<checksum> (Toy-Stil, analog N(I))."""

from __future__ import annotations

from gpm_types.ci.substance import prime_for_char

BIG_PRIME = 982451653


def checksum_c(value: str) -> int:
    """Positionsabhängige Prüfsumme über die Zeichen (Reihenfolge zählt)."""
    if not value:
        raise ValueError("Leerer C(I)-Wert.")
    h = 1
    for i, ch in enumerate(value):
        # Positionsgewicht (i+1) macht die Prüfsumme reihenfolgesensitiv,
        # sodass =>/>= verschiedene Checksums bekommen.
        h = (h * pow(prime_for_char(ch), i + 1, BIG_PRIME)) % BIG_PRIME
    return h


def pointer_id_c(value: str) -> str:
    return f"C_{checksum_c(value)}"
