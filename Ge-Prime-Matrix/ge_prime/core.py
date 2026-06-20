"""Kernkonfiguration — feste Primzahl-Map (27 Zeichen) und Permutationsraum."""

import math
from collections import Counter

# Permutationsraum N = L! / (k1! * k2! * …) — Anzahl lexikographischer Anordnungen
PRIME_MAP = {
    'A': 3, 'B': 59, 'C': 29, 'D': 31, 'E': 2, 'F': 61, 'G': 53, 'H': 47,
    'I': 7, 'J': 97, 'K': 73, 'L': 23, 'M': 41, 'N': 13, 'O': 5, 'P': 43,
    'Q': 101, 'R': 17, 'S': 19, 'T': 11, 'U': 37, 'V': 79, 'W': 71,
    'X': 83, 'Y': 67, 'Z': 89, 'ß': 103
}

# Umkehr-Mapping für die verlustfreie Dekompression (Faktorisierung)
CHAR_MAP = {v: k for k, v in PRIME_MAP.items()}


def calc_total_perms(counts: Counter) -> int:
    """
    Berechnet die exakte Kardinalität (Multinominalkoeffizient)
    für eine gegebene Multimenge an Zeichen.
    """
    total_len = sum(counts.values())
    denom = 1
    for c in counts.values():
        denom *= math.factorial(c)
    return math.factorial(total_len) // denom
