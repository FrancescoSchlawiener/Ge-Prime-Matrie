"""Tests für profil-aware Prime-Profile (Invariante A)."""

import unittest

from alphabets import AlphabetProfile
from alphabets.registry import prime_map_for_profile
from analysis.compile.compiler import compile_text
from analysis.profile.prime_profile import build_prime_profile, profile_overlap


class TestPrimeProfileOG(unittest.TestCase):
    DE_TEXT = "Der Patient erhält eine Diagnose."

    def test_prime_profile_og_alpha(self):
        doc, _ = compile_text(self.DE_TEXT, AlphabetProfile.OG)
        profile = build_prime_profile(doc)
        self.assertGreater(sum(profile.values()), 0)
        prime_map = prime_map_for_profile(AlphabetProfile.OG)
        self.assertIn(prime_map["E"], profile)

    def test_profile_overlap_identical(self):
        doc, _ = compile_text(self.DE_TEXT, AlphabetProfile.OG)
        profile = build_prime_profile(doc)
        self.assertGreaterEqual(profile_overlap(profile, profile), 0.99)


class TestPrimeProfileArabic(unittest.TestCase):
    def test_prime_profile_arabic_skeleton(self):
        doc, _ = compile_text("مرحبا", AlphabetProfile.ARABIC)
        profile = build_prime_profile(doc)
        self.assertGreater(sum(profile.values()), 0)
        prime_map = prime_map_for_profile(AlphabetProfile.ARABIC)
        self.assertEqual(len(prime_map), 28)


class TestPrimeProfileAmharic(unittest.TestCase):
    def test_prime_profile_amharic(self):
        doc, _ = compile_text("ሰላም", AlphabetProfile.AMHARIC)
        profile = build_prime_profile(doc)
        self.assertGreater(sum(profile.values()), 0)
        prime_map = prime_map_for_profile(AlphabetProfile.AMHARIC)
        self.assertEqual(len(prime_map), 34)


class TestPrimeProfileCrossScript(unittest.TestCase):
    def test_same_romanized_concept_different_profiles(self):
        """OG vs Roman — gleiche lateinische Zeichen, identische Prime-Profile."""
        text = "HALLO"
        og_doc, _ = compile_text(text, AlphabetProfile.OG)
        roman_doc, _ = compile_text(text, AlphabetProfile.ROMAN)
        og_profile = build_prime_profile(og_doc)
        roman_profile = build_prime_profile(roman_doc)
        self.assertEqual(dict(og_profile), dict(roman_profile))

    def test_arabic_vs_og_different_prime_sets(self):
        og_doc, _ = compile_text("HALLO", AlphabetProfile.OG)
        ar_doc, _ = compile_text("مرحبا", AlphabetProfile.ARABIC)
        og_keys = set(build_prime_profile(og_doc))
        ar_keys = set(build_prime_profile(ar_doc))
        self.assertNotEqual(og_keys, ar_keys)


if __name__ == "__main__":
    unittest.main()
