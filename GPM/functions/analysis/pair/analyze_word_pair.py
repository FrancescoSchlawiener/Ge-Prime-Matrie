"""Wortpaar-Analyse — Encode, Klassifikation und Vergleich."""

from __future__ import annotations

from alphabets import AlphabetProfile
from analysis.algebra.substance_kernel import compare_substances
from analysis.substance.diff import classify_word_pair
from alphabets.normalize import prepare_substrate
from gpm_types.si import encode_si


def analyze_word_pair(
    word1: str,
    word2: str,
    profile: AlphabetProfile | str = AlphabetProfile.OG,
) -> dict:
    if isinstance(profile, str):
        profile = AlphabetProfile(profile)

    s1, i1 = encode_si(word1, profile)
    s2, i2 = encode_si(word2, profile)
    norm1 = prepare_substrate(word1, profile)
    norm2 = prepare_substrate(word2, profile)

    classification = classify_word_pair(
        s1,
        s2,
        i1,
        i2,
        profile,
        norm_len1=len(norm1),
        norm_len2=len(norm2),
    )
    comparison = compare_substances(s1, s2, profile)

    return {
        "word1": word1,
        "word2": word2,
        "substance1": s1,
        "substance2": s2,
        "perm_index1": i1,
        "perm_index2": i2,
        "classification": classification,
        "comparison": comparison,
    }
