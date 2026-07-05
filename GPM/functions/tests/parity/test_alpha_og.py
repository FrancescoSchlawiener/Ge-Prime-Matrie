import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
OG_ROOT = ROOT.parent.parent / "Ge-Prime-Matrix OG"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(OG_ROOT))

from alpha_og import ALPHA_OG, CHAR_OG
from ge_prime.core import CHAR_MAP, PRIME_MAP


class TestAlphaOg(unittest.TestCase):
    def test_matches_og_prime_map_bitgenau(self):
        self.assertEqual(ALPHA_OG, PRIME_MAP)

    def test_char_og_matches_og(self):
        self.assertEqual(CHAR_OG, CHAR_MAP)

    def test_27_symbols(self):
        self.assertEqual(len(ALPHA_OG), 27)

    def test_lex_order_covers_all(self):
        from alpha_og import ALPHA_OG_LEX_ORDER
        self.assertEqual(set(ALPHA_OG_LEX_ORDER), set(ALPHA_OG.keys()))


if __name__ == "__main__":
    unittest.main()
