"""Gemeinsame Perm-Invarianten-Helfer für Tests und perm_audit CLI."""

from __future__ import annotations

from collections import Counter

from alphabets.lex import lex_order_for_profile
from alphabets.normalize import prepare_substrate
from alphabets.profiles import AlphabetProfile
from gpm_types.si.codec import decode_si, encode_si
from gpm_types.si.order import Sp
from tools.benchmark_patterns import build_unique, can_build_pattern

CURATED_ANAGRAMS: dict[AlphabetProfile, tuple[str, str]] = {
    AlphabetProfile.OG: ("HALLO", "OLLAH"),
    AlphabetProfile.ROMAN: ("HALLO", "OLLAH"),
    AlphabetProfile.GREEK: ("ΑΒΓ", "ΓΒΑ"),
    AlphabetProfile.CYRILLIC: ("АБВ", "ВБА"),
}


def anagram_pair_for_profile(profile: AlphabetProfile) -> tuple[str, str] | None:
    if profile in CURATED_ANAGRAMS:
        return CURATED_ANAGRAMS[profile]
    if not can_build_pattern(profile, 3, "unique"):
        return None
    seq = build_unique(lex_order_for_profile(profile), 3)
    return seq, seq[::-1]


def check_anagram_invariant(profile: AlphabetProfile, word_a: str, word_b: str) -> str | None:
    seq_a = prepare_substrate(word_a, profile)
    seq_b = prepare_substrate(word_b, profile)
    if Counter(seq_a) != Counter(seq_b):
        return "Multiset ungleich nach Normalisierung"
    if seq_a == seq_b:
        return "Keine echte Permutation (seq identisch)"

    s_a, i_a = encode_si(word_a, profile)
    s_b, i_b = encode_si(word_b, profile)
    if s_a != s_b:
        return f"S unterscheidet sich ({s_a} != {s_b})"
    if i_a == i_b:
        return f"I gleich bei Anagramm ({i_a})"
    if decode_si(s_a, i_a, profile) != seq_a:
        return "decode A fehlgeschlagen"
    if decode_si(s_b, i_b, profile) != seq_b:
        return "decode B fehlgeschlagen"
    if Sp(seq_a, profile) == Sp(seq_b, profile):
        return "Sp gleich bei Anagramm"
    return None
