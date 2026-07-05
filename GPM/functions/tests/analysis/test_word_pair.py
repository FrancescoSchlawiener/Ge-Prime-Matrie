"""Tests für analyze_word_pair."""

import unittest

from alphabets import AlphabetProfile
from analysis.pair.analyze_word_pair import analyze_word_pair


class TestWordPair(unittest.TestCase):
    def test_listen_silent(self):
        result = analyze_word_pair("LISTEN", "SILENT", AlphabetProfile.OG)
        self.assertTrue(result["classification"]["is_anagram"])
        self.assertAlmostEqual(result["comparison"]["ggt_kgv_similarity"], 1.0, places=6)

    def test_hallo_ollah(self):
        result = analyze_word_pair("HALLO", "OLLAH", AlphabetProfile.OG)
        self.assertTrue(result["classification"]["is_anagram"])
        self.assertAlmostEqual(result["comparison"]["ggt_kgv_similarity"], 1.0, places=6)

    def test_identical(self):
        result = analyze_word_pair("HALLO", "HALLO", AlphabetProfile.OG)
        self.assertTrue(result["classification"]["is_identical"])


if __name__ == "__main__":
    unittest.main()
