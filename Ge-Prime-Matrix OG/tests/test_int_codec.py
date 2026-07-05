import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ge_prime.core import calc_total_perms
from collections import Counter

from gpm.int_codec import (
    WIDTH_CLASSES,
    decode_fixed_int,
    encode_fixed_int,
    perm_space_size,
    perm_width_class,
    perm_width_bytes,
    substance_width_class,
    token_byte_len,
    width_bytes_for_class,
    width_class_for_magnitude,
    width_class_label,
)
from gpm.model import GpmHeaderEntry


class TestIntCodec(unittest.TestCase):
    def test_width_classes_are_powers_of_two_from_2(self):
        self.assertEqual(WIDTH_CLASSES, (2, 4, 8, 16))

    def test_width_class_for_magnitude_boundaries(self):
        self.assertEqual(width_class_for_magnitude(1), 0)
        self.assertEqual(width_class_for_magnitude(65535), 0)
        self.assertEqual(width_class_for_magnitude(65536), 1)
        self.assertEqual(width_class_for_magnitude(2**32 - 1), 1)
        self.assertEqual(width_class_for_magnitude(2**32), 2)

    def test_substance_hallo_class(self):
        # HALLO substance = 372945 (>65535 → Stufe 1 = 4 B)
        self.assertEqual(substance_width_class(372945), 1)
        self.assertEqual(width_bytes_for_class(substance_width_class(372945)), 4)

    def test_perm_hallo_welt_classes(self):
        self.assertEqual(perm_space_size("HALLO"), 60)
        self.assertEqual(perm_width_class("HALLO"), 0)
        self.assertEqual(perm_width_bytes("HALLO"), 2)
        self.assertEqual(perm_space_size("WELT"), 24)
        self.assertEqual(perm_width_bytes("WELT"), 2)

    def test_perm_thirteen_letters_exceeds_u32_space(self):
        word = "ABCDEFGHIJKLM"
        n = calc_total_perms(Counter(word))
        self.assertGreater(n, 2**32)
        self.assertEqual(perm_width_class(word), 2)
        self.assertEqual(perm_width_bytes(word), 8)

    def test_encode_decode_roundtrip(self):
        for value in (1, 255, 372945, 65536, 2**32):
            wclass = width_class_for_magnitude(value)
            width = width_bytes_for_class(wclass)
            blob = encode_fixed_int(value, width)
            self.assertEqual(decode_fixed_int(blob, width), value)

    def test_encode_rejects_overflow(self):
        with self.assertRaises(ValueError):
            encode_fixed_int(65536, 2)

    def test_token_byte_len(self):
        header = [
            GpmHeaderEntry(0, "hallo", "HALLO", 372945),
            GpmHeaderEntry(1, "welt", "WELT", 123),
        ]
        self.assertEqual(token_byte_len(word_id=0, header=header), 5)
        self.assertEqual(token_byte_len(word_id=1, header=header), 5)

    def test_width_class_label(self):
        self.assertEqual(width_class_label(0), "2 B")


if __name__ == "__main__":
    unittest.main()
