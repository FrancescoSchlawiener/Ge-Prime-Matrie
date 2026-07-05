"""Tests für die Case-Schicht."""

import unittest

from analysis.case.apply import apply_case
from analysis.case.codes import CASE_EXPLICIT, CASE_LOWER, CASE_TITLE, CASE_UPPER
from analysis.case.detect import detect_case


class TestCase(unittest.TestCase):
    def test_detect_lower(self):
        self.assertEqual(detect_case("hallo"), CASE_LOWER)

    def test_detect_upper(self):
        self.assertEqual(detect_case("HALLO"), CASE_UPPER)

    def test_detect_title(self):
        self.assertEqual(detect_case("Hallo"), CASE_TITLE)

    def test_detect_explicit(self):
        self.assertEqual(detect_case("HaLlo"), CASE_EXPLICIT)

    def test_eszett_lower(self):
        self.assertEqual(apply_case("straße", CASE_LOWER), "straße")
        self.assertEqual(apply_case("straße", CASE_UPPER), "STRAẞE")

    def test_eszett_title(self):
        self.assertEqual(apply_case("straße", CASE_TITLE), "Straße")

    def test_roundtrip_modes(self):
        for word in ("hallo", "HALLO", "Hallo"):
            code = detect_case(word)
            if code != CASE_EXPLICIT:
                self.assertEqual(apply_case(apply_case(word, CASE_LOWER), code), word)

    def test_explicit_roundtrip(self):
        word = "StRaßE"
        code = detect_case(word)
        self.assertEqual(code, CASE_EXPLICIT)


if __name__ == "__main__":
    unittest.main()
