"""Wort-/Permutations-Algebra ohne Perm-LUT-Explosion."""

from __future__ import annotations

import hashlib
from collections import Counter

from alphabets import AlphabetProfile
from gpm_types.si.substance import ingredients_for_profile
from perm.multiset import perm_fits_width, perm_space

from analysis.algebra.substance_kernel import compare_substances


def substance_quotient_ingredients(
    a: int,
    b: int,
    profile: AlphabetProfile | str,
) -> Counter[str]:
    cmp = compare_substances(a, b, profile if isinstance(profile, AlphabetProfile) else AlphabetProfile(profile))
    return Counter(cmp["unique_to_first"])


def anagram_class_key(substance: int, profile: AlphabetProfile | str) -> int:
    """Stabiler Bucket aus sortierten Ingredient-Exponents."""
    if substance <= 1:
        return 0
    prof = profile if isinstance(profile, AlphabetProfile) else AlphabetProfile(profile)
    ingredients = ingredients_for_profile(substance, prof)
    parts = sorted(f"{char}:{count}" for char, count in ingredients.items())
    digest = hashlib.sha256("|".join(parts).encode()).hexdigest()
    return int(digest[:16], 16)


def perm_compatible(
    a_sub: int,
    b_sub: int,
    profile: AlphabetProfile | str,
) -> bool:
    """Schneller Vorcheck: gleiche Länge/Breite ohne LUT-Bau."""
    prof = profile if isinstance(profile, AlphabetProfile) else AlphabetProfile(profile)
    ing_a = ingredients_for_profile(a_sub, prof)
    ing_b = ingredients_for_profile(b_sub, prof)
    if sum(ing_a.values()) != sum(ing_b.values()):
        return False
    n_a = perm_space(Counter(ing_a))
    n_b = perm_space(Counter(ing_b))
    if n_a != n_b:
        return False
    return perm_fits_width(n_a) and perm_fits_width(n_b)
