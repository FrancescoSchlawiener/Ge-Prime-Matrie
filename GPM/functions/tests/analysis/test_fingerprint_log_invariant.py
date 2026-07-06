"""Härtungs-Invariante E-A — fingerprint_similarity mit profile → kein Integer-LCM."""

import unittest
from unittest.mock import patch

from alphabets import AlphabetProfile
from analysis.algebra.window_fold import ExponentWindow
from analysis.index.substance_index import _fingerprint_lcm_value, fingerprint_similarity


class TestFingerprintLogInvariant(unittest.TestCase):
    def test_profile_path_skips_lcm(self):
        a = ExponentWindow({2: 4, 3: 2})
        b = ExponentWindow({2: 3, 5: 1})
        with patch(
            "analysis.index.substance_index._fingerprint_lcm_value",
            side_effect=AssertionError("Integer-LCM forbidden when profile is set"),
        ):
            score = fingerprint_similarity(a, b, profile=AlphabetProfile.OG)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_profile_path_matches_window_similarity(self):
        from analysis.algebra.window_fold import window_similarity

        a = ExponentWindow({2: 5, 7: 1})
        b = ExponentWindow({2: 4, 7: 2})
        direct, _ = window_similarity(a, b, profile_a=AlphabetProfile.OG, profile_b=AlphabetProfile.OG)
        via_fp = fingerprint_similarity(a, b, profile=AlphabetProfile.OG)
        self.assertAlmostEqual(via_fp, direct)

    def test_legacy_path_uses_lcm_when_no_profile(self):
        a = ExponentWindow({2: 2})
        b = ExponentWindow({2: 2})
        sa = _fingerprint_lcm_value(a)
        sb = _fingerprint_lcm_value(b)
        score = fingerprint_similarity(a, b, profile=None)
        self.assertAlmostEqual(score, 1.0)
        self.assertEqual(sa, sb)


if __name__ == "__main__":
    unittest.main()
