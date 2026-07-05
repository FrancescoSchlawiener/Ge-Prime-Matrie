import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from alphabets.greek.map import ALPHA_GREEK, CHAR_GREEK_SET
from alphabets.roman.normalize import prepare_substrate
from alphabets.profiles import AlphabetProfile
from gpm_types.si.substance import substance_for_profile


class TestGreek(unittest.TestCase):
    def test_map_size(self):
        self.assertEqual(len(ALPHA_GREEK), 24)

    def test_omega_in_set(self):
        self.assertIn("Ω", CHAR_GREEK_SET)

    def test_omega_not_roman(self):
        from alphabets.roman.map import CHAR_ROMAN
        self.assertNotIn("Ω", CHAR_ROMAN)

    def test_substance_alpha(self):
        seq = prepare_substrate("ΑΘΗΝΑ", AlphabetProfile.GREEK)
        s = substance_for_profile(seq, AlphabetProfile.GREEK)
        self.assertGreater(s, 1)


if __name__ == "__main__":
    unittest.main()
