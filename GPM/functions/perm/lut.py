"""Permutations-LUT — pro Multimenge materialisiert."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from functools import lru_cache

from alphabets.roman.map import ALPHA_ROMAN_LEX_ORDER
from perm.multiset import perm_decode, perm_space

MAX_LUT_BUILD_LENGTH = 12


@dataclass(frozen=True)
class PermutationLut:
    counts_signature: tuple[tuple[str, int], ...]
    entries: tuple[str, ...]

    @property
    def perm_space(self) -> int:
        return len(self.entries)

    def sequence_at(self, index: int) -> str:
        if index < 1 or index > len(self.entries):
            raise ValueError(f"Index {index} außerhalb LUT (N={len(self.entries)}).")
        return self.entries[index - 1]

    def index_of(self, sequence: str) -> int:
        try:
            return self.entries.index(sequence) + 1
        except ValueError as exc:
            raise ValueError(f"Sequenz {sequence!r} nicht in LUT.") from exc


def counts_signature(counts: Counter[str]) -> tuple[tuple[str, int], ...]:
    return tuple(sorted(counts.items()))


def _assert_lut_buildable(counts: Counter[str]) -> None:
    total = sum(counts.values())
    if total > MAX_LUT_BUILD_LENGTH:
        raise ValueError(
            f"Multimenge Länge {total} überschreitet MAX_LUT_BUILD_LENGTH={MAX_LUT_BUILD_LENGTH}."
        )


def build_permutation_lut(counts: Counter[str]) -> PermutationLut:
    _assert_lut_buildable(counts)
    n = perm_space(counts)
    entries = tuple("".join(perm_decode(counts, i)) for i in range(1, n + 1))
    return PermutationLut(counts_signature=counts_signature(counts), entries=entries)


def build_permutation_lut_for_sequence(sequence: str) -> PermutationLut:
    return build_permutation_lut(Counter(sequence))


@lru_cache(maxsize=256)
def _cached_lut(signature: tuple[tuple[str, int], ...]) -> PermutationLut:
    return build_permutation_lut(Counter(dict(signature)))


def get_permutation_lut(counts: Counter[str]) -> PermutationLut:
    return _cached_lut(counts_signature(counts))


def lut_sequence_at_index(lut: PermutationLut, index: int) -> str:
    return lut.sequence_at(index)


def lut_index_of_sequence(lut: PermutationLut, sequence: str) -> int:
    return lut.index_of(sequence)


def sequence_identity_from_lut(lut: PermutationLut, index: int) -> tuple[str, ...]:
    return tuple(lut.sequence_at(index))


def build_singleton_lut(symbol: str) -> PermutationLut:
    if symbol not in ALPHA_ROMAN_LEX_ORDER:
        raise ValueError(f"Symbol {symbol!r} nicht im Roman-Alpha-Satz.")
    return build_permutation_lut(Counter({symbol: 1}))


ALPHA_ROMAN_SINGLETON_LUTS: dict[str, PermutationLut] = {
    sym: build_singleton_lut(sym) for sym in ALPHA_ROMAN_LEX_ORDER
}
