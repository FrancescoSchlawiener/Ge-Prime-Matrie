import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from alphabets import AlphabetProfile
from analysis.binary.format import read_gpm
from analysis.binary.search import search_by_gcd, search_by_word
from analysis.compile.compiler import compile_text_to_gpm


class TestBinarySearch(unittest.TestCase):
    def setUp(self):
        _, self.blob, _ = compile_text_to_gpm("Francesco Francesco Schauer Straße", AlphabetProfile.OG)

    def test_search_exact_substance(self):
        doc = read_gpm(self.blob)
        hit = search_by_word(doc, "Francesco")
        self.assertTrue(hit["found_in_header"])
        self.assertEqual(hit["occurrences"], 2)

    def test_search_missing_word(self):
        doc = read_gpm(self.blob)
        hit = search_by_word(doc, "XYZABC")
        self.assertFalse(hit["found_in_header"])

    def test_gcd_filter_finds_shared_letters(self):
        doc = read_gpm(self.blob)
        result = search_by_gcd(doc, "Straße")
        self.assertGreaterEqual(result["unique_words"], 1)


if __name__ == "__main__":
    unittest.main()
