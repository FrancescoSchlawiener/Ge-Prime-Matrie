"""Primzahl-Profile für Dokumente — profil-aware (Invariante A)."""

from __future__ import annotations

from collections import Counter

from alphabets import AlphabetProfile
from alphabets.registry import prime_map_for_profile
from analysis.document.model import GpmDocument
from gpm_types.si.substance import ingredients_for_profile


from analysis.algebra.sparse_counter import counter_overlap as profile_overlap


def word_frequencies(document: GpmDocument) -> Counter:
    counts: Counter = Counter()
    for token in document.tokens:
        counts[token.word_id] += 1
    return counts


def ingredients_to_profile(
    ingredients: Counter[str],
    profile: AlphabetProfile | str,
    *,
    multiplier: int = 1,
) -> Counter[int]:
    prime_map = prime_map_for_profile(profile)
    result: Counter[int] = Counter()
    for char, count in ingredients.items():
        prime = prime_map.get(char)
        if prime:
            result[prime] += count * multiplier
    return result


def build_prime_profile(document: GpmDocument) -> Counter[int]:
    freqs = word_frequencies(document)
    profile: Counter[int] = Counter()
    for word_id, count in freqs.items():
        entry = document.header[word_id]
        ingredients = ingredients_for_profile(entry.substance, document.profile)
        profile.update(ingredients_to_profile(ingredients, document.profile, multiplier=count))
    return profile


# profile_overlap: re-export from algebra.sparse_counter (Phase E3)
