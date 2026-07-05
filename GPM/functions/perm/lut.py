"""Permutations-LUT — pro Multimenge materialisiert; Lazy-Singletons für Nicht-Roman."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from functools import lru_cache

from alphabets.profiles import AlphabetProfile
from alphabets.registry import lex_order_for_profile
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


_SINGLETON_LUTS: dict[AlphabetProfile, dict[str, PermutationLut]] = {}


def counts_signature(counts: Counter[str]) -> tuple[tuple[str, int], ...]:
    return tuple(sorted(counts.items()))


def _assert_lut_buildable(counts: Counter[str]) -> None:
    total = sum(counts.values())
    if total > MAX_LUT_BUILD_LENGTH:
        raise ValueError(
            f"Multimenge Länge {total} überschreitet MAX_LUT_BUILD_LENGTH={MAX_LUT_BUILD_LENGTH}."
        )


def build_permutation_lut(
    counts: Counter[str],
    lex_order: Sequence[str] | None = None,
) -> PermutationLut:
    _assert_lut_buildable(counts)
    n = perm_space(counts)
    entries = tuple(
        "".join(perm_decode(counts, i, lex_order=lex_order)) for i in range(1, n + 1)
    )
    return PermutationLut(counts_signature=counts_signature(counts), entries=entries)


def build_permutation_lut_for_sequence(
    sequence: str,
    profile: AlphabetProfile | str | None = None,
) -> PermutationLut:
    lex = lex_order_for_profile(profile) if profile is not None else None
    return build_permutation_lut(Counter(sequence), lex_order=lex)


@lru_cache(maxsize=512)
def _cached_lut(
    signature: tuple[tuple[str, int], ...],
    profile_value: str | None,
) -> PermutationLut:
    lex = lex_order_for_profile(profile_value) if profile_value else None
    return build_permutation_lut(Counter(dict(signature)), lex_order=lex)


def get_permutation_lut(
    counts: Counter[str],
    profile: AlphabetProfile | str | None = None,
) -> PermutationLut:
    profile_value = profile.value if isinstance(profile, AlphabetProfile) else profile
    return _cached_lut(counts_signature(counts), profile_value)


def lut_sequence_at_index(lut: PermutationLut, index: int) -> str:
    return lut.sequence_at(index)


def lut_index_of_sequence(lut: PermutationLut, sequence: str) -> int:
    return lut.index_of(sequence)


def sequence_identity_from_lut(lut: PermutationLut, index: int) -> tuple[str, ...]:
    return tuple(lut.sequence_at(index))


def build_singleton_lut(
    symbol: str,
    profile: AlphabetProfile | str = AlphabetProfile.ROMAN,
) -> PermutationLut:
    if isinstance(profile, str):
        profile = AlphabetProfile(profile)
    lex = lex_order_for_profile(profile)
    if symbol not in lex:
        raise ValueError(f"Symbol {symbol!r} nicht im Alpha-Satz ({profile.value!r}).")
    return build_permutation_lut(Counter({symbol: 1}), lex_order=lex)


def _ensure_profile_singleton_luts(profile: AlphabetProfile) -> dict[str, PermutationLut]:
    if profile is AlphabetProfile.ROMAN:
        return ALPHA_ROMAN_SINGLETON_LUTS
    if profile not in _SINGLETON_LUTS:
        lex = lex_order_for_profile(profile)
        _SINGLETON_LUTS[profile] = {
            sym: build_singleton_lut(sym, profile) for sym in lex
        }
    return _SINGLETON_LUTS[profile]


def get_singleton_lut(symbol: str, profile: AlphabetProfile | str) -> PermutationLut:
    if isinstance(profile, str):
        profile = AlphabetProfile(profile)
    return _ensure_profile_singleton_luts(profile)[symbol]


ALPHA_ROMAN_SINGLETON_LUTS: dict[str, PermutationLut] = {
    sym: build_singleton_lut(sym, AlphabetProfile.ROMAN) for sym in ALPHA_ROMAN_LEX_ORDER
}
