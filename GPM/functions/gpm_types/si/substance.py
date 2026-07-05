"""Substanz S — OG-Pfad (Parität) und profilabhängige Substanz."""

from __future__ import annotations

from collections import Counter

from alphabets.profiles import AlphabetProfile
from alphabets.registry import char_map_for_profile, prime_map_for_profile
from alphabets.normalize import prepare_substrate


def substance_for_profile(sequence: str, profile: AlphabetProfile | str) -> int:
    seq = prepare_substrate(sequence, profile)
    prime_map = prime_map_for_profile(profile)
    s = 1
    for char in seq:
        if char not in prime_map:
            raise ValueError(f"Symbol {char!r} nicht im Profil {profile!r}.")
        s *= prime_map[char]
    return s


def ingredients_for_profile(substance: int, profile: AlphabetProfile | str) -> Counter[str]:
    counts: Counter[str] = Counter()
    char_map = char_map_for_profile(profile)
    for prime in sorted(char_map.keys()):
        char = char_map[prime]
        while substance % prime == 0:
            counts[char] += 1
            substance //= prime
    if substance != 1:
        raise ValueError(f"S={substance} konnte nicht vollständig faktorisiert werden ({profile!r}).")
    return counts


def substance_og_alpha(sequence: str) -> int:
    return substance_for_profile(sequence, AlphabetProfile.OG)


def ingredients_og_alpha(substance: int) -> Counter[str]:
    return ingredients_for_profile(substance, AlphabetProfile.OG)


def substance_roman(sequence: str) -> int:
    return substance_for_profile(sequence, AlphabetProfile.ROMAN)


def ingredients_roman(substance: int) -> Counter[str]:
    return ingredients_for_profile(substance, AlphabetProfile.ROMAN)


get_substance = substance_og_alpha
get_ingredients = ingredients_og_alpha


def S(sequence: str, profile: AlphabetProfile | str = AlphabetProfile.OG) -> int:
    if profile in (AlphabetProfile.OG, "og"):
        return substance_og_alpha(sequence)
    return substance_for_profile(sequence, profile)
