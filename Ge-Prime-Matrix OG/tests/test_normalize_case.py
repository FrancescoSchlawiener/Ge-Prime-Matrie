import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ge_prime.decode import decode_word
from ge_prime.encode import encode_word
from gpm.compiler import compile_text
from pipeline.normalize import (
    CASE_EXPLICIT,
    CASE_LOWER,
    CASE_TITLE,
    CASE_UPPER,
    apply_case,
    detect_case,
    normalize_text_nfc,
    normalize_word,
)


class TestEszett(unittest.TestCase):
    def test_eszett_roundtrip(self):
        for word in ("STRAßE", "GROEßE", "ßPAß", "MAßE"):
            substance, index = encode_word(word)
            self.assertEqual(decode_word(substance, index), word)

    def test_eszett_not_expanded(self):
        self.assertEqual(normalize_word("Straße"), "STRAßE")
        self.assertNotEqual(normalize_word("Straße"), normalize_word("Strasse"))


class TestDetectCase(unittest.TestCase):
    def test_lower(self):
        self.assertEqual(detect_case("haus"), CASE_LOWER)
        self.assertEqual(detect_case("straße"), CASE_LOWER)

    def test_title(self):
        self.assertEqual(detect_case("Haus"), CASE_TITLE)
        self.assertEqual(detect_case("Straße"), CASE_TITLE)

    def test_upper(self):
        self.assertEqual(detect_case("HAUS"), CASE_UPPER)
        self.assertEqual(detect_case("STRAẞE"), CASE_UPPER)

    def test_explicit(self):
        self.assertEqual(detect_case("McDonald"), CASE_EXPLICIT)
        self.assertEqual(detect_case("iPhone"), CASE_EXPLICIT)


class TestApplyCase(unittest.TestCase):
    def test_roundtrip_all_states(self):
        for run in ("haus", "Haus", "HAUS", "straße", "Straße"):
            code = detect_case(run)
            if code == CASE_EXPLICIT:
                continue
            canonical = apply_case(run, CASE_LOWER)
            self.assertEqual(apply_case(canonical, code), run)

    def test_eszett_upper_uses_capital_eszett(self):
        # ß → ẞ statt SS bei Großschreibung
        self.assertEqual(apply_case("straße", CASE_UPPER), "STRAẞE")
        self.assertEqual(apply_case("straße", CASE_TITLE), "Straße")
        self.assertEqual(apply_case("straße", CASE_LOWER), "straße")


class TestNormalizeTextNfc(unittest.TestCase):
    def test_nfd_and_nfc_same_token_count(self):
        nfc = "Gr\u00e4ser"
        nfd = "Gr\u0061\u0308ser"
        doc_nfc, _, stats_nfc = compile_text(normalize_text_nfc(nfc))
        doc_nfd, _, stats_nfd = compile_text(normalize_text_nfc(nfd))
        self.assertEqual(stats_nfc.total_tokens, stats_nfd.total_tokens)

    def test_selection_clamp_after_nfc_no_index_error(self):
        from ge_prime.spectroscope import spectroscope_from_text

        nfd = "a\u0308bc"
        nfc_len = len(normalize_text_nfc(nfd))
        result = spectroscope_from_text(
            nfd,
            selection_start=0,
            selection_end=nfc_len + 5,
            modes=["anagram_shadow"],
        )
        self.assertIn("target", result)

    def test_crlf_normalized_to_lf(self):
        text = "Erster Absatz.\r\n\r\nZweiter Absatz."
        normalized = normalize_text_nfc(text)
        self.assertNotIn("\r", normalized)
        self.assertIn("\n\n", normalized)
        doc, _, _ = compile_text(normalized)
        from ge_prime.hierarchy import build_document_hierarchy

        h = build_document_hierarchy(doc)
        self.assertEqual(len(h.semantic.paragraphs), 2)


if __name__ == "__main__":
    unittest.main()
