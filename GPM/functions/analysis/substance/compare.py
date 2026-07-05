"""ggT, kgV und Ähnlichkeit zweier Substanzen — profil-aware."""

from __future__ import annotations

import math
from collections import Counter

from alphabets import AlphabetProfile
from gpm_types.si.substance import ingredients_for_profile


def substance_lcm(s1: int, s2: int) -> int:
    if s1 < 1 or s2 < 1:
        raise ValueError("Substanz muss >= 1 sein.")
    return math.lcm(s1, s2)


def substance_covers(container: int, required: int) -> bool:
    if required < 1:
        raise ValueError("Erforderliche Substanz muss >= 1 sein.")
    if container < 1:
        return False
    return container % required == 0


def union_letters(s1: int, s2: int, profile: AlphabetProfile) -> dict:
    lcm_value = substance_lcm(s1, s2)
    return dict(ingredients_for_profile(lcm_value, profile)) if lcm_value > 1 else {}


def substance_ggt_kgv_similarity(s1: int, s2: int) -> float:
    gcd_val = math.gcd(s1, s2)
    if gcd_val <= 1 or s1 <= 1 or s2 <= 1:
        return 0.0
    lcm_val = math.lcm(s1, s2)
    ln_gcd = math.log(gcd_val)
    ln_kgv = math.log(lcm_val)
    if ln_kgv <= 0:
        return 0.0
    return ln_gcd / ln_kgv


def substance_ggt_kgv_distance(s1: int, s2: int) -> float:
    return 1.0 - substance_ggt_kgv_similarity(s1, s2)


def compare_substances(s1: int, s2: int, profile: AlphabetProfile) -> dict:
    gcd_value = math.gcd(s1, s2)
    shared = ingredients_for_profile(gcd_value, profile) if gcd_value > 1 else Counter()

    s1_unique = _relative_ingredients(s1, gcd_value, profile)
    s2_unique = _relative_ingredients(s2, gcd_value, profile)

    lcm_value = substance_lcm(s1, s2)
    union = ingredients_for_profile(lcm_value, profile) if lcm_value > 1 else Counter()

    smaller = min(s1, s2)
    legacy_similarity = gcd_value / smaller if smaller > 0 else 0.0
    ggt_kgv_sim = substance_ggt_kgv_similarity(s1, s2)

    return {
        "gcd_value": gcd_value,
        "lcm_value": lcm_value,
        "kgv_value": lcm_value,
        "shared_letters": dict(shared),
        "union_letters": dict(union),
        "unique_to_first": dict(s1_unique),
        "unique_to_second": dict(s2_unique),
        "similarity_ratio": round(legacy_similarity, 6),
        "legacy_similarity_ratio": round(legacy_similarity, 6),
        "ggt_kgv_similarity": round(ggt_kgv_sim, 6),
    }


def _relative_ingredients(value: int, divisor: int, profile: AlphabetProfile) -> Counter:
    if divisor <= 0 or value <= 0:
        return Counter()
    quotient = value // divisor
    return ingredients_for_profile(quotient, profile) if quotient > 1 else Counter()
