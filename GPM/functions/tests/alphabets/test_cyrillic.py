import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from alphabets.cyrillic.map import ALPHA_CYRILLIC, CHAR_CYRILLIC_SET
from alphabets.roman.normalize import prepare_substrate
from alphabets.profiles import AlphabetProfile
from gpm_types.si.substance import substance_for_profile


class TestCyrillic(unittest.TestCase):
    def test_map_size(self):
        self.assertEqual(len(ALPHA_CYRILLIC), 33)

    def test_cyrillic_a_in_set(self):
        self.assertIn("А", CHAR_CYRILLIC_SET)

    def test_cyrillic_not_roman(self):
        from alphabets.roman.map import CHAR_ROMAN
        self.assertNotIn("А", CHAR_ROMAN)

    def test_substance_cyrillic(self):
        seq = prepare_substrate("ПРИВЕТ", AlphabetProfile.CYRILLIC)
        s = substance_for_profile(seq, AlphabetProfile.CYRILLIC)
        self.assertGreater(s, 1)


if __name__ == "__main__":
    unittest.main()
