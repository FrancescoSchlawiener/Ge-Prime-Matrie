"""Gemeinsame Multiset-Permutations-Engine (Wort- und Zell-Ebene)."""

from __future__ import annotations

from collections import Counter
from typing import Hashable, TypeVar

from ge_prime.core import calc_total_perms

_WIDTH_CLASSES = (2, 4, 8, 16)


def _width_bytes_for_magnitude(value: int) -> int:
    if value < 1:
        raise ValueError("Wert muss >= 1 sein.")
    bits = value.bit_length()
    if bits <= 16:
        return _WIDTH_CLASSES[0]
    if bits <= 32:
        return _WIDTH_CLASSES[1]
    if bits <= 64:
        return _WIDTH_CLASSES[2]
    return _WIDTH_CLASSES[3]

T = TypeVar("T", bound=Hashable)


def perm_space(counts: Counter) -> int:
    """Kardinalität N des Permutationsraums für eine Multimenge."""
    if not counts:
        return 1
    return calc_total_perms(counts)


def perm_index(sequence: list[T], counts: Counter[T]) -> int:
    """
    1-basierter lexikographischer Rang von ``sequence`` in ``counts``.
    ``sequence`` muss exakt die Multimenge ``counts`` permutieren.
    """
    working = Counter(counts)
    if sum(working.values()) != len(sequence):
        raise ValueError("Sequenzlänge passt nicht zur Multimenge.")
    index = 1
    for symbol in sequence:
        if working[symbol] <= 0:
            raise ValueError(f"Symbol {symbol!r} nicht in Multimenge verfügbar.")
        smaller = sorted(s for s in working.keys() if s < symbol)
        for sc in smaller:
            working[sc] -= 1
            index += calc_total_perms(working)
            working[sc] += 1
        working[symbol] -= 1
        if working[symbol] == 0:
            del working[symbol]
    return index


def perm_decode(counts: Counter[T], index: int) -> list[T]:
    """Rekonstruiert die Permutation aus Multimenge und 1-basiertem Index."""
    if index < 1:
        raise ValueError("Index muss >= 1 sein.")
    working = Counter(counts)
    total_len = sum(working.values())
    if total_len == 0:
        if index != 1:
            raise ValueError("Leere Multimenge erlaubt nur Index 1.")
        return []
    n = perm_space(working)
    if index > n:
        raise ValueError(f"Index {index} außerhalb des Raums N={n}.")

    result: list[T] = []
    remaining = index
    for _ in range(total_len):
        for symbol in sorted(working.keys()):
            working[symbol] -= 1
            block = calc_total_perms(working)
            if remaining > block:
                remaining -= block
                working[symbol] += 1
            else:
                result.append(symbol)
                if working[symbol] == 0:
                    del working[symbol]
                break
        else:
            raise ValueError("Index konnte nicht dekodiert werden.")
    return result


def perm_fits_width(n: int, max_bytes: int = 16) -> bool:
    """True wenn N und jeder Index 1..N in max_bytes Byte passen."""
    if n < 1:
        return False
    try:
        return _width_bytes_for_magnitude(n) <= max_bytes
    except ValueError:
        return False
