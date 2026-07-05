"""Tests für Substanz-Differenz und Wortpaar-Klassifikation."""

import unittest

from alphabets import AlphabetProfile
from analysis.substance.diff import classify_word_pair, diff_substances
from gpm_types.si import encode_si


class TestSubstanceDiff(unittest.TestCase):
    def setUp(self):
        self.profile = AlphabetProfile.OG

    def test_listen_silent_anagram(self):
        s1, i1 = encode_si("LISTEN", self.profile)
        s2, i2 = encode_si("SILENT", self.profile)
        result = classify_word_pair(s1, s2, i1, i2, self.profile)
        self.assertTrue(result["is_anagram"])
        self.assertFalse(result["is_identical"])

    def test_identical_pair(self):
        s1, i1 = encode_si("HALLO", self.profile)
        s2, i2 = encode_si("HALLO", self.profile)
        result = classify_word_pair(s1, s2, i1, i2, self.profile)
        self.assertTrue(result["is_identical"])
        self.assertFalse(result["is_anagram"])

    def test_subset_detection(self):
        s_at, _ = encode_si("AT", self.profile)
        s_cat, _ = encode_si("CAT", self.profile)
        diff = diff_substances(s_at, s_cat, self.profile)
        self.assertTrue(diff["is_subset_1_in_2"])


if __name__ == "__main__":
    unittest.main()
