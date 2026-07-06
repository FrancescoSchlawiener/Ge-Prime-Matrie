"""Tests für prime_minhash — Härtungs-Invariante A."""

import unittest
from collections import Counter

from alphabets import AlphabetProfile
from analysis.algebra.minhash import minhash_band_distance, prime_minhash


class TestMinhash(unittest.TestCase):
    def test_different_exponents_different_hash(self):
        a = Counter({2: 1, 3: 1})
        b = Counter({2: 2, 3: 1})
        ha = prime_minhash(a, alphabet_profile=AlphabetProfile.OG)
        hb = prime_minhash(b, alphabet_profile=AlphabetProfile.OG)
        self.assertNotEqual(ha, hb)

    def test_profile_salt_changes_hash(self):
        profile = Counter({2: 2})
        og = prime_minhash(profile, alphabet_profile=AlphabetProfile.OG)
        greek = prime_minhash(profile, alphabet_profile=AlphabetProfile.GREEK)
        self.assertNotEqual(og, greek)

    def test_doubled_exponents_longer_vector(self):
        base = Counter({5: 1, 7: 1})
        doubled = Counter({5: 2, 7: 2})
        self.assertGreaterEqual(len(prime_minhash(doubled, alphabet_profile=AlphabetProfile.OG)), len(
            prime_minhash(base, alphabet_profile=AlphabetProfile.OG)
        ))

    def test_band_distance_jaccard(self):
        a = (1, 2, 3, 4)
        b = (3, 4, 5, 6)
        self.assertAlmostEqual(minhash_band_distance(a, b), 2 / 6, places=6)
        self.assertEqual(minhash_band_distance(None, a), 0.0)


if __name__ == "__main__":
    unittest.main()
