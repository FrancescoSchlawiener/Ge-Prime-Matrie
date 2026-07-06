"""Blocker-Tests — Härtungs-Invariante D-C (profile_symmetry_guard first)."""

import unittest

from alphabets import AlphabetProfile
from analysis.algebra.sparse_counter import counter_cosine_guarded, counter_jaccard_guarded
from analysis.algebra.window_fold import ExponentWindow, compare_windows_pair, window_similarity
from analysis.compile.compiler import compile_text


class TestGuardAudit(unittest.TestCase):
    def test_window_similarity_profile_mismatch(self):
        w = ExponentWindow({2: 1, 3: 1})
        score, reason = window_similarity(
            w,
            w,
            profile_a=AlphabetProfile.OG,
            profile_b=AlphabetProfile.CYRILLIC,
        )
        self.assertEqual(score, 0.0)
        self.assertEqual(reason, "profile_mismatch")

    def test_compare_windows_pair_mismatch(self):
        w = ExponentWindow({2: 1})
        gate = compare_windows_pair(
            w,
            w,
            profile_a=AlphabetProfile.OG,
            profile_b=AlphabetProfile.GREEK,
        )
        self.assertFalse(gate.passed)
        self.assertEqual(gate.zero_reason, "profile_mismatch")

    def test_counter_cosine_guarded_mismatch(self):
        from collections import Counter

        c = Counter({2: 1})
        score, reason = counter_cosine_guarded(
            c,
            c,
            profile_a=AlphabetProfile.OG,
            profile_b=AlphabetProfile.CYRILLIC,
        )
        self.assertEqual(score, 0.0)
        self.assertEqual(reason, "profile_mismatch")

    def test_counter_jaccard_guarded_same_profile_ok(self):
        from collections import Counter

        doc_a, _ = compile_text("Test", AlphabetProfile.OG)
        doc_b, _ = compile_text("Test", AlphabetProfile.OG)
        from analysis.profile.relation import build_relation_profile

        rel_a = build_relation_profile(doc_a)
        rel_b = build_relation_profile(doc_b)
        score, reason = counter_jaccard_guarded(
            rel_a["word_bigrams"],
            rel_b["word_bigrams"],
            profile_a=AlphabetProfile.OG,
            profile_b=AlphabetProfile.OG,
        )
        self.assertIsNone(reason)
        self.assertGreaterEqual(score, 0.0)


if __name__ == "__main__":
    unittest.main()
