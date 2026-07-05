"""Decode — Substanz S und Index I → Wort; Faktorisierung der Buchstaben-Zutatenliste."""
from collections import Counter

from ge_prime.core import CHAR_MAP
from ge_prime.multiset_geom import perm_decode


def get_ingredients(substance_value: int) -> Counter:
    """
    Verlustfreie Dekompression: Faktorisierung des Substanzwertes S,
    um die exakte atomare Zutatenliste zu rekonstruieren.
    """
    counts = Counter()
    for prime, char in sorted(CHAR_MAP.items()):
        while substance_value % prime == 0:
            counts[char] += 1
            substance_value //= prime
    return counts


def decode_word(substance_value: int, index: int) -> str:
    """
    Rekonstruiert das Wort exakt aus S (Substanz) und I (Index).
    Macht aus dem Datenobjekt S(I) wieder die geometrische Anordnung.
    """
    counts = get_ingredients(substance_value)
    chars = perm_decode(counts, index)
    return "".join(chars)
