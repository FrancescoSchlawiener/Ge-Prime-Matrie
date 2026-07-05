"""Encode — Wort → Substanz S (Primzahlprodukt) und Index I (Permutations-Rang)."""
from collections import Counter

from ge_prime.core import PRIME_MAP
from ge_prime.multiset_geom import perm_index


def _eszett_safe_upper(word: str) -> str:
    """Großschreibung, die ß erhält (Pythons upper() würde ß→SS machen)."""
    return "".join(ch if ch == "ß" else ch.upper() for ch in word)


def get_substance(word: str) -> int:
    """
    Berechnet den kollisionsfreien Substanzwert S (Primzahlprodukt).
    Die Reihenfolge der Zeichen wird hierbei mathematisch ignoriert.
    """
    word = _eszett_safe_upper(word)
    s = 1
    for char in word:
        if char in PRIME_MAP:
            s *= PRIME_MAP[char]
    return s


def get_index(word: str) -> int:
    """
    Berechnet den Permutations-Index I über fraktale Intervallschachtelung.
    Ermittelt die exakte Position des Wortes im lexikographisch sortierten Suchraum.
    """
    word = _eszett_safe_upper(word)
    counts = Counter(word)
    return perm_index(list(word), counts)


def encode_word(word: str) -> tuple[int, int]:
    """
    Hauptfunktion für den Encoder.
    Gibt ein Tuple (S, I) zurück.
    """
    return get_substance(word), get_index(word)
