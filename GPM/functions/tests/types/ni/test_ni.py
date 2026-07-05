import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from gpm_types.ni.canonical import canonical_n
from gpm_types.ni.codec import encode_ni, decode_ni
from gpm_types.ni.registry import NRegistry
from gpm_types.ni.substance import substance_n


class TestNi(unittest.TestCase):
    def test_canonical_strips_leading_zeros(self):
        self.assertEqual(canonical_n("007"), "7")
        self.assertEqual(canonical_n("0"), "0")

    def test_canonical_rejects_negative(self):
        with self.assertRaises(ValueError):
            canonical_n("-1")

    def test_canonical_rejects_non_digit(self):
        with self.assertRaises(ValueError):
            canonical_n("12a")

    def test_substance_zero(self):
        self.assertEqual(substance_n("0"), 2)

    def test_substance_differs_for_different_values(self):
        self.assertNotEqual(substance_n("123"), substance_n("124"))

    def test_registry_roundtrip(self):
        reg = NRegistry()
        pid = reg.register("42")
        self.assertTrue(pid.startswith("N_"))
        self.assertEqual(decode_ni(pid, reg), "42")

    def test_encode_ni(self):
        s, pid = encode_ni("99")
        self.assertGreater(s, 1)
        self.assertTrue(pid.startswith("N_"))


if __name__ == "__main__":
    unittest.main()
