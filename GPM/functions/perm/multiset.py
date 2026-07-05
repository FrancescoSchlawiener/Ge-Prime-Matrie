"""Permutations-Engine — lexikographischer Rang und Unrank."""

from __future__ import annotations

import math as _stdlib_math
from collections import Counter
from typing import Hashable, Sequence, TypeVar

_WIDTH_CLASSES = (2, 4, 8, 16)
T = TypeVar("T", bound=Hashable)


def calc_total_perms(counts: Counter) -> int:
    total_len = sum(counts.values())
    if total_len == 0:
        return 1
    denom = 1
    for c in counts.values():
        denom *= _stdlib_math.factorial(c)
    return _stdlib_math.factorial(total_len) // denom


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


def perm_space(counts: Counter[T]) -> int:
    if not counts:
        return 1
    return calc_total_perms(counts)


def _rank_map(lex_order: Sequence[T] | None) -> dict[T, int] | None:
    if lex_order is None:
        return None
    return {sym: i for i, sym in enumerate(lex_order)}


def _symbols_by_rank(keys: set[T], rank: dict[T, int] | None) -> list[T]:
    if rank is None:
        return sorted(keys)
    missing = keys - rank.keys()
    if missing:
        raise ValueError(f"Symbole fehlen in lex_order: {sorted(missing)!r}")
    return sorted(keys, key=lambda s: rank[s])


def _is_lex_smaller(a: T, b: T, rank: dict[T, int] | None) -> bool:
    if rank is None:
        return a < b  # type: ignore[operator]
    return rank[a] < rank[b]


def perm_index(
    sequence: list[T],
    counts: Counter[T],
    lex_order: Sequence[T] | None = None,
) -> int:
    rank = _rank_map(lex_order)
    working = Counter(counts)
    if sum(working.values()) != len(sequence):
        raise ValueError("Sequenzlänge passt nicht zur Multimenge.")
    index = 1
    for symbol in sequence:
        if working[symbol] <= 0:
            raise ValueError(f"Symbol {symbol!r} nicht in Multimenge verfügbar.")
        smaller = [
            s for s in working.keys()
            if s != symbol and _is_lex_smaller(s, symbol, rank)
        ]
        for sc in sorted(smaller, key=lambda s: rank[s] if rank else s):
            working[sc] -= 1
            index += calc_total_perms(working)
            working[sc] += 1
        working[symbol] -= 1
        if working[symbol] == 0:
            del working[symbol]
    return index


def perm_decode(
    counts: Counter[T],
    index: int,
    lex_order: Sequence[T] | None = None,
) -> list[T]:
    if index < 1:
        raise ValueError("Index muss >= 1 sein.")
    rank = _rank_map(lex_order)
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
        for symbol in _symbols_by_rank(set(working.keys()), rank):
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
    if n < 1:
        return False
    try:
        return _width_bytes_for_magnitude(n) <= max_bytes
    except ValueError:
        return False
