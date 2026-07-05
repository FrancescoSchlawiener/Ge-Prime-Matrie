import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from gpm_types.hi.codec import encode_hi, decode_hi, hi_fingerprint
from gpm_types.hi.segments import parse_hi_segments


class TestHi(unittest.TestCase):
    def test_segment_order_reading_order(self):
        payload = parse_hi_segments("ABC123")
        self.assertEqual(payload.segments[0].tag, "S")
        self.assertEqual(payload.segments[0].value, "ABC")
        self.assertEqual(payload.segments[1].tag, "N")
        self.assertEqual(payload.segments[1].value, "123")

    def test_abc123_not_equal_123abc(self):
        _, s1 = encode_hi("ABC123")
        _, s2 = encode_hi("123ABC")
        self.assertNotEqual(s1, s2)
        self.assertNotEqual(hi_fingerprint("ABC123"), hi_fingerprint("123ABC"))

    def test_roundtrip(self):
        raw = "HALLO42"
        payload, _ = encode_hi(raw)
        self.assertEqual(decode_hi(payload), "HALLO42")

    def test_rejects_pure_s(self):
        with self.assertRaises(ValueError):
            parse_hi_segments("HALLO")

    def test_rejects_pure_n(self):
        with self.assertRaises(ValueError):
            parse_hi_segments("123")


if __name__ == "__main__":
    unittest.main()
