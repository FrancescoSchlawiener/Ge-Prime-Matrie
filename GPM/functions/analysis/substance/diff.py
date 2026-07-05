"""Arithmetische Differenz zweier Substanzen."""

from __future__ import annotations

import math

from alphabets import AlphabetProfile
from gpm_types.si.substance import ingredients_for_profile


def substance_remainder(dividend: int, gcd_value: int) -> int:
    if gcd_value < 1:
        raise ValueError("ggT muss >= 1 sein.")
    if dividend < 1:
        raise ValueError("Substanz muss >= 1 sein.")
    if dividend % gcd_value != 0:
        raise ValueError("Substanz ist nicht durch ggT teilbar.")
    return dividend // gcd_value


def remainder_letters(remainder: int, profile: AlphabetProfile) -> dict:
    if remainder <= 1:
        return {}
    return dict(ingredients_for_profile(remainder, profile))


def diff_substances(s1: int, s2: int, profile: AlphabetProfile) -> dict:
    if s1 < 1 or s2 < 1:
        raise ValueError("Substanz muss >= 1 sein.")

    gcd_value = math.gcd(s1, s2)
    remainder_s1 = substance_remainder(s1, gcd_value)
    remainder_s2 = substance_remainder(s2, gcd_value)

    return {
        "gcd_value": gcd_value,
        "remainder_s1": remainder_s1,
        "remainder_s2": remainder_s2,
        "remainder_letters_s1": remainder_letters(remainder_s1, profile),
        "remainder_letters_s2": remainder_letters(remainder_s2, profile),
        "is_subset_1_in_2": remainder_s1 == 1 and s1 != s2,
        "is_subset_2_in_1": remainder_s2 == 1 and s1 != s2,
        "is_same_substance": s1 == s2,
    }


def classify_word_pair(
    s1: int,
    s2: int,
    perm_index1: int,
    perm_index2: int,
    profile: AlphabetProfile,
    *,
    norm_len1: int | None = None,
    norm_len2: int | None = None,
) -> dict:
    result = diff_substances(s1, s2, profile)
    result["is_anagram"] = s1 == s2 and perm_index1 != perm_index2
    result["is_identical"] = s1 == s2 and perm_index1 == perm_index2
    if norm_len1 is not None and norm_len2 is not None:
        result["same_length"] = norm_len1 == norm_len2
    return result
