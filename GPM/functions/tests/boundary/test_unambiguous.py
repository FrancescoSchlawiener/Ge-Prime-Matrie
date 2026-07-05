import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from gpm_types.classify import PayloadKind, classify_token
from gpm_types.hi.codec import encode_hi
from gpm_types.ni.codec import encode_ni
from gpm_types.si.codec import encode


class TestUnambiguous(unittest.TestCase):
    def test_classify_s(self):
        self.assertEqual(classify_token("HALLO"), PayloadKind.S)

    def test_classify_n(self):
        self.assertEqual(classify_token("123"), PayloadKind.N)

    def test_classify_d(self):
        self.assertEqual(classify_token("4,16"), PayloadKind.D)

    def test_classify_h(self):
        self.assertEqual(classify_token("ABC123"), PayloadKind.H)

    def test_s_not_h(self):
        s, _ = encode("HALLO")
        with self.assertRaises(ValueError):
            encode_hi("HALLO")

    def test_n_not_h(self):
        with self.assertRaises(ValueError):
            encode_hi("123")

    def test_h_order_collision(self):
        _, a = encode_hi("A1B2")
        _, b = encode_hi("1A2B")
        self.assertNotEqual(a, b)


if __name__ == "__main__":
    unittest.main()
