import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
OG_ROOT = ROOT.parent.parent / "Ge-Prime-Matrix OG"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(OG_ROOT))

from alpha_roman import AlphabetProfile
from preparation import prepare_substrate
from si import decode, decode_si_og, decode_via_lut, decode_word, encode, encode_si_og, encode_word, get_index, permutation_index_via_lut
from ge_prime.decode import decode_word as og_decode_word
from ge_prime.encode import encode_word as og_encode_word


class TestSiOg(unittest.TestCase):
    def test_roundtrip(self):
        for word in ("HALLO", "FRANCESCO", "STRAßE", "Straße", "Strauß", "Größe"):
            s, i = encode(word)
            self.assertEqual(decode(s, i), prepare_substrate(word, AlphabetProfile.OG))

    def test_matches_og_aliases(self):
        for word in ("HALLO", "LISTEN", "Straße", "Strauß", "Größe"):
            prepared = prepare_substrate(word, AlphabetProfile.OG)
            og_s, og_i = og_encode_word(prepared)
            self.assertEqual(encode_word(word), (og_s, og_i))
            self.assertEqual(decode_word(og_s, og_i), og_decode_word(og_s, og_i))

    def test_eszett_not_same_as_ss(self):
        s_eszett, i_eszett = encode("Straße")
        s_ss, i_ss = encode("Strasse")
        self.assertNotEqual((s_eszett, i_eszett), (s_ss, i_ss))
        self.assertEqual(decode(s_eszett, i_eszett), "STRAßE")
        self.assertEqual(decode(s_ss, i_ss), "STRASSE")

    def test_lut_index_matches_get_index(self):
        for word in ("HALLO", "PAPA"):
            seq = prepare_substrate(word, AlphabetProfile.OG)
            self.assertEqual(permutation_index_via_lut(seq), get_index(word))

    def test_decode_via_lut(self):
        s, i = encode("HALLO")
        self.assertEqual(decode_via_lut(s, i), decode(s, i))


if __name__ == "__main__":
    unittest.main()
