import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
OG_ROOT = ROOT.parent.parent / "Ge-Prime-Matrix OG"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(OG_ROOT))

from alpha_roman import AlphabetProfile
from preparation import prepare_substrate
from substrate_og import S, get_substance, substance_og_alpha, substance_roman
from ge_prime.encode import get_substance as og_get_substance


class TestSubstrateOg(unittest.TestCase):
    def test_s_hallo_matches_og(self):
        self.assertEqual(S("HALLO"), og_get_substance("HALLO"))
        self.assertEqual(get_substance("HALLO"), og_get_substance("HALLO"))

    def test_s_anagram_same(self):
        self.assertEqual(S("LISTEN"), S("SILENT"))

    def test_roman_equals_og_for_latin(self):
        self.assertEqual(substance_roman("HALLO"), substance_og_alpha("HALLO"))

    def test_eszett_raw_input_matches_og_pipeline(self):
        for word in ("Straße", "Strauß", "Größe", "straße"):
            normalized = prepare_substrate(word, AlphabetProfile.OG)
            self.assertEqual(S(word), og_get_substance(normalized))
            self.assertIn("ß", normalized)

    def test_eszett_differs_from_ss(self):
        self.assertNotEqual(S("Straße"), S("Strasse"))
        self.assertNotEqual(
            substance_og_alpha("STRAßE"),
            substance_og_alpha("STRASSE"),
        )

    def test_eszett_prime_103_in_factorization(self):
        from alpha_og import ALPHA_OG

        s = S("Straße")
        self.assertEqual(s % ALPHA_OG["ß"], 0)
        s_ss = S("Strasse")
        self.assertNotEqual(s_ss % ALPHA_OG["ß"], 0)


if __name__ == "__main__":
    unittest.main()
