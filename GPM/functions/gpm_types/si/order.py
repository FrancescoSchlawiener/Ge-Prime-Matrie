"""Reihenfolge-Modus — Sk, Sp, Lut (getrennt vom kommutativen S)."""

from __future__ import annotations

from collections import Counter

from alphabets.profiles import AlphabetProfile
from alphabets.roman.map import prime_map_for_profile
from perm.lut import (
    PermutationLut,
    build_permutation_lut_for_sequence,
    get_permutation_lut,
    lut_index_of_sequence,
    sequence_identity_from_lut,
)

_POSITION_WEIGHTS: tuple[int, ...] = (
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
    73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157,
    163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241,
    251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311,
)


def sequence_identity(sequence: str) -> tuple[str, ...]:
    return tuple(sequence)


def permutation_lut_for_sequence(sequence: str) -> PermutationLut:
    return build_permutation_lut_for_sequence(sequence)


def sequence_key_via_lut(sequence: str) -> tuple[PermutationLut, int]:
    lut = get_permutation_lut(Counter(sequence))
    return lut, lut_index_of_sequence(lut, sequence)


def substance_positional(
    sequence: str,
    profile: AlphabetProfile | str = AlphabetProfile.ROMAN,
) -> int:
    if not sequence:
        return 1
    prime_map = prime_map_for_profile(profile)
    result = 1
    for i, char in enumerate(sequence):
        if char not in prime_map:
            raise ValueError(f"Symbol {char!r} nicht im Alpha-Profil {profile!r}.")
        if i >= len(_POSITION_WEIGHTS):
            raise ValueError(
                f"Sequenz zu lang für Positions-Gewichte (max {len(_POSITION_WEIGHTS)} Symbole)."
            )
        result *= prime_map[char] ** _POSITION_WEIGHTS[i]
    return result


def Sk(sequence: str) -> tuple[str, ...]:
    return sequence_identity(sequence)


def Sk_lut(sequence: str) -> tuple[str, ...]:
    lut, idx = sequence_key_via_lut(sequence)
    return sequence_identity_from_lut(lut, idx)


def Sp(sequence: str, profile: AlphabetProfile | str = AlphabetProfile.ROMAN) -> int:
    return substance_positional(sequence, profile)


def Lut(sequence: str) -> PermutationLut:
    return permutation_lut_for_sequence(sequence)
