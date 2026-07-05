import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from gpm_types.di.relation import parse_decimal, relation_key
from gpm_types.di.codec import encode_di, decode_di_relation


class TestDi(unittest.TestCase):
    def test_416_german_comma(self):
        rel = parse_decimal("4,16")
        self.assertEqual(rel.as_triple(), (4, 25, 4))
        self.assertEqual(relation_key("4,16"), "4:25:4")

    def test_416_dot(self):
        self.assertEqual(encode_di("4.16"), (4, 25, 4))

    def test_integer_decimal(self):
        self.assertEqual(encode_di("4"), (4, 1, 1))

    def test_zero_decimal(self):
        rel = parse_decimal("0,0")
        self.assertEqual(rel.whole, 0)

    def test_roundtrip(self):
        for raw in ("4,16", "1,0", "0,01", "3,5"):
            rel = parse_decimal(raw)
            self.assertEqual(decode_di_relation(rel), raw)

    def test_rejects_negative(self):
        with self.assertRaises(ValueError):
            parse_decimal("-1,5")

    def test_ggt_one(self):
        rel = parse_decimal("1,3")
        self.assertEqual(rel.ggt, 1)


if __name__ == "__main__":
    unittest.main()
