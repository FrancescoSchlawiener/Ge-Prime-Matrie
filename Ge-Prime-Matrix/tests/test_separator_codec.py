import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from gpm.separator_codec import (
    SEP_PERM_E,
    SEP_PERM_S,
    SEP_PERM_Z,
    decode_gaps,
    encode_gaps,
    perm_code_label,
    scan_perm_code,
)


class TestSeparatorCodec(unittest.TestCase):
    def test_perm_zero_for_plain_text(self):
        gaps = ["", " ", ""]
        self.assertEqual(scan_perm_code(gaps), 0)
        self.assertEqual(perm_code_label(0), "BASE (Leerzeichen & Satzzeichen)")

    def test_perm_digits_and_symbols(self):
        gaps = ["", " ", "99€", ""]
        perm = scan_perm_code(gaps)
        self.assertEqual(perm, SEP_PERM_Z | SEP_PERM_S)

    def test_perm_emoji(self):
        gaps = ["", " 🎉", ""]
        self.assertEqual(scan_perm_code(gaps), SEP_PERM_E)

    def test_encode_decode_roundtrip_base(self):
        gaps = ["", " ", " ", ""]
        perm = scan_perm_code(gaps)
        blob = encode_gaps(gaps, perm)
        self.assertLess(len(blob), sum(4 + len(g.encode()) for g in gaps))
        decoded = decode_gaps(blob, perm, len(gaps))
        self.assertEqual(decoded, gaps)

    def test_encode_decode_punctuation(self):
        gaps = ["", ", ", "!"]
        perm = scan_perm_code(gaps)
        decoded = decode_gaps(encode_gaps(gaps, perm), perm, len(gaps))
        self.assertEqual(decoded, gaps)

    def test_encode_decode_digits_symbol_emoji(self):
        text_gaps = ["", ": ", "99€ 🎉", ""]
        perm = scan_perm_code(text_gaps)
        self.assertEqual(perm, SEP_PERM_Z | SEP_PERM_S | SEP_PERM_E)
        decoded = decode_gaps(encode_gaps(text_gaps, perm), perm, len(text_gaps))
        self.assertEqual(decoded, text_gaps)

    def test_empty_gaps_minimal_blob(self):
        gaps = ["", ""]
        perm = 0
        blob = encode_gaps(gaps, perm)
        self.assertEqual(decode_gaps(blob, perm, 2), ["", ""])

    def test_perm_label_combined(self):
        label = perm_code_label(SEP_PERM_Z | SEP_PERM_S | SEP_PERM_E)
        self.assertIn("Ziffern", label)
        self.assertIn("Symbole", label)
        self.assertIn("Emoji", label)

    def test_underscore_snake_case_roundtrip(self):
        gaps = ["", "_", ""]
        perm = scan_perm_code(gaps)
        self.assertEqual(perm, 0)
        decoded = decode_gaps(encode_gaps(gaps, perm), perm, len(gaps))
        self.assertEqual(decoded, gaps)

    def test_unknown_symbol_uses_unicode_perm(self):
        gaps = ["", "‽", ""]
        perm = scan_perm_code(gaps)
        from gpm.separator_codec import SEP_PERM_U

        self.assertTrue(perm & SEP_PERM_U)
        decoded = decode_gaps(encode_gaps(gaps, perm), perm, len(gaps))
        self.assertEqual(decoded, gaps)


if __name__ == "__main__":
    unittest.main()
