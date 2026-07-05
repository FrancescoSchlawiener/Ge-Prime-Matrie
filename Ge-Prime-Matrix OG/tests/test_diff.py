import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ge_prime.diff import (
    classify_word_pair,
    diff_substances,
    remainder_letters,
    substance_remainder,
)
from ge_prime.encode import encode_word


class TestSubstanceDiff(unittest.TestCase):
    def test_at_cat_subset(self):
        s_at, _ = encode_word("AT")
        s_cat, _ = encode_word("CAT")
        diff = diff_substances(s_at, s_cat)
        self.assertEqual(diff["remainder_s1"], 1)
        self.assertTrue(diff["is_subset_1_in_2"])
        self.assertFalse(diff["is_subset_2_in_1"])
        self.assertEqual(diff["remainder_letters_s1"], {})

    def test_cat_at_reverse(self):
        s_at, _ = encode_word("AT")
        s_cat, _ = encode_word("CAT")
        diff = diff_substances(s_cat, s_at)
        self.assertEqual(diff["remainder_s2"], 1)
        self.assertTrue(diff["is_subset_2_in_1"])
        self.assertFalse(diff["is_subset_1_in_2"])
        self.assertEqual(set(diff["remainder_letters_s1"].keys()), {"C"})

    def test_listen_silent_anagram(self):
        s1, i1 = encode_word("LISTEN")
        s2, i2 = encode_word("SILENT")
        cls = classify_word_pair(s1, s2, i1, i2, norm_len1=6, norm_len2=6)
        self.assertTrue(cls["is_same_substance"])
        self.assertTrue(cls["is_anagram"])
        self.assertFalse(cls["is_identical"])
        self.assertTrue(cls["same_length"])

    def test_hallo_identical(self):
        s1, i1 = encode_word("HALLO")
        s2, i2 = encode_word("HALLO")
        cls = classify_word_pair(s1, s2, i1, i2)
        self.assertTrue(cls["is_identical"])
        self.assertFalse(cls["is_anagram"])
        self.assertFalse(cls["is_subset_1_in_2"])
        self.assertFalse(cls["is_subset_2_in_1"])

    def test_anagram_not_marked_as_subset(self):
        s1, i1 = encode_word("LISTEN")
        s2, i2 = encode_word("SILENT")
        cls = classify_word_pair(s1, s2, i1, i2)
        self.assertTrue(cls["is_anagram"])
        self.assertFalse(cls["is_subset_1_in_2"])
        self.assertFalse(cls["is_subset_2_in_1"])

    def test_diff_matches_compare_unique_letters(self):
        from ge_prime.compare import compare_substances

        s1, i1 = encode_word("SCHAUER")
        s2, i2 = encode_word("SCHULE")
        cmp = compare_substances(s1, s2)
        diff = classify_word_pair(s1, s2, i1, i2)
        self.assertEqual(cmp["unique_to_first"], diff["remainder_letters_s1"])
        self.assertEqual(cmp["unique_to_second"], diff["remainder_letters_s2"])
        self.assertEqual(diff["remainder_s1"] * cmp["gcd_value"], s1)
        self.assertEqual(diff["remainder_s2"] * cmp["gcd_value"], s2)

    def test_disjoint_words_no_subset(self):
        s1, i1 = encode_word("ABC")
        s2, i2 = encode_word("XYZ")
        diff = diff_substances(s1, s2)
        self.assertEqual(diff["gcd_value"], 1)
        self.assertFalse(diff["is_subset_1_in_2"])
        self.assertFalse(diff["is_subset_2_in_1"])

    def test_substance_remainder_rejects_invalid(self):
        with self.assertRaises(ValueError):
            substance_remainder(0, 1)
        with self.assertRaises(ValueError):
            substance_remainder(6, 0)

    def test_remainder_letters_empty_for_one(self):
        self.assertEqual(remainder_letters(1), {})


if __name__ == "__main__":
    unittest.main()
