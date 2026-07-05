"""Permutations-Identität und Anagramm-Invariante für alle 33 Profile."""

from __future__ import annotations

import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alphabets.lex import lex_order_for_profile
from alphabets.normalize import prepare_substrate
from alphabets.profiles import AlphabetProfile
from alphabets.registry import all_profiles
from gpm_types.si.codec import encode_si, permutation_index_for_profile
from gpm_types.si.order import Sk_lut, sequence_key_via_lut
from perm.lut import get_permutation_lut, lut_index_of_sequence
from perm.multiset import perm_index
from tools.benchmark_patterns import build_unique, can_build_pattern
from tools.perm_invariants import anagram_pair_for_profile, check_anagram_invariant


class TestPermIdentityAllProfiles(unittest.TestCase):
    def test_anagram_invariant_all_profiles(self) -> None:
        for profile in all_profiles():
            pair = anagram_pair_for_profile(profile)
            if pair is None:
                self.skipTest(f"{profile.name}: kein 3-Zeichen-Anagramm baubar")
            word_a, word_b = pair
            err = check_anagram_invariant(profile, word_a, word_b)
            self.assertIsNone(err, f"{profile.name}: {err}")

    def test_perm_index_discriminates_reversal_all_profiles(self) -> None:
        for profile in all_profiles():
            if not can_build_pattern(profile, 3, "unique"):
                self.skipTest(f"{profile.name}: unique L=3 nicht baubar")
            seq = build_unique(lex_order_for_profile(profile), 3)
            rev = seq[::-1]
            lex = lex_order_for_profile(profile)
            counts = Counter(seq)
            idx_a = perm_index(list(seq), counts, lex_order=lex)
            idx_b = perm_index(list(rev), counts, lex_order=lex)
            self.assertNotEqual(idx_a, idx_b, profile.name)

    def test_encode_i_matches_perm_index_all_profiles(self) -> None:
        for profile in all_profiles():
            if not can_build_pattern(profile, 3, "unique"):
                continue
            raw = build_unique(lex_order_for_profile(profile), 3)
            seq = prepare_substrate(raw, profile)
            _, i_enc = encode_si(raw, profile)
            i_perm = permutation_index_for_profile(seq, profile)
            self.assertEqual(i_enc, i_perm, profile.name)

    def test_lut_cascade_consistency_all_profiles(self) -> None:
        for profile in all_profiles():
            if not can_build_pattern(profile, 3, "unique"):
                continue
            raw = build_unique(lex_order_for_profile(profile), 3)
            seq = prepare_substrate(raw, profile)
            if len(seq) > 12:
                continue
            _, i_enc = encode_si(raw, profile)
            i_lut = sequence_key_via_lut(seq, profile)[1]
            i_perm = permutation_index_for_profile(seq, profile)
            self.assertEqual(i_lut, i_perm, profile.name)
            self.assertEqual(i_lut, i_enc, profile.name)
            self.assertEqual(Sk_lut(seq, profile), tuple(seq), profile.name)

    def test_greek_lex_differs_from_codepoint_fallback(self) -> None:
        profile = AlphabetProfile.GREEK
        seq = build_unique(lex_order_for_profile(profile), 3)
        lut_fallback = get_permutation_lut(Counter(seq))
        idx_fallback = lut_index_of_sequence(lut_fallback, seq)
        idx_profile = sequence_key_via_lut(seq, profile)[1]
        self.assertNotEqual(idx_fallback, idx_profile)


if __name__ == "__main__":
    unittest.main()
