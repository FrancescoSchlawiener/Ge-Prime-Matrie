import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from alpha_og import ALPHA_OG, CHAR_OG
from alpha_roman import (
    ALPHA_ROMAN,
    CHAR_ROMAN,
    PRIME_TO_CHAR_ROMAN,
    prime_map_for_profile,
    AlphabetProfile,
)


class TestAlphaRoman(unittest.TestCase):
    def test_derived_from_og(self):
        self.assertEqual(ALPHA_ROMAN, ALPHA_OG)

    def test_prime_to_char_inversion(self):
        self.assertEqual(PRIME_TO_CHAR_ROMAN, CHAR_OG)
        for sym, prime in ALPHA_ROMAN.items():
            self.assertEqual(PRIME_TO_CHAR_ROMAN[prime], sym)

    def test_char_roman_is_frozenset(self):
        self.assertIsInstance(CHAR_ROMAN, frozenset)
        self.assertEqual(CHAR_ROMAN, frozenset(ALPHA_ROMAN.keys()))

    def test_omega_not_in_char_roman(self):
        self.assertNotIn("Ω", CHAR_ROMAN)

    def test_profiles(self):
        self.assertEqual(prime_map_for_profile(AlphabetProfile.OG), ALPHA_OG)
        self.assertEqual(prime_map_for_profile(AlphabetProfile.ROMAN), ALPHA_ROMAN)


if __name__ == "__main__":
    unittest.main()
