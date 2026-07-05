"""Tests für Compile, Gap-Symmetrie und Rekonstruktion."""

import unittest

from alphabets import AlphabetProfile
from analysis.case.policy import CaseStoragePolicy
from analysis.compile.compiler import compile_text
from analysis.compile.reconstruct import reconstruct_text
from analysis.document.invariants import assert_gap_symmetry


class TestCompile(unittest.TestCase):
    def setUp(self):
        self.profile = AlphabetProfile.OG

    def _roundtrip(self, source: str, *, store_case: bool = True) -> None:
        policy = CaseStoragePolicy(store_case=store_case)
        doc, _ = compile_text(source, self.profile, case_policy=policy)
        assert_gap_symmetry(doc)
        if store_case:
            self.assertEqual(reconstruct_text(doc), source)
        else:
            self.assertEqual(reconstruct_text(doc), source.lower())

    def test_hallo_welt_gaps(self):
        doc, _ = compile_text("Hallo Welt", self.profile)
        assert_gap_symmetry(doc)
        self.assertEqual(doc.gaps, ["", " ", ""])
        self.assertEqual(len(doc.tokens), 2)
        self.assertEqual(reconstruct_text(doc), "Hallo Welt")

    def test_leading_gap(self):
        doc, _ = compile_text(" Hallo", self.profile)
        self.assertEqual(doc.gaps[0], " ")
        self.assertEqual(reconstruct_text(doc), " Hallo")

    def test_trailing_gap(self):
        doc, _ = compile_text("Hallo ", self.profile)
        self.assertEqual(doc.gaps[-1], " ")
        self.assertEqual(reconstruct_text(doc), "Hallo ")

    def test_comma_before_word(self):
        doc, _ = compile_text(",Hallo", self.profile)
        self.assertEqual(doc.gaps[0], ",")
        self.assertEqual(reconstruct_text(doc), ",Hallo")

    def test_comma_between_words(self):
        doc, _ = compile_text("Hallo,Welt", self.profile)
        self.assertEqual(doc.gaps[1], ",")
        self.assertEqual(reconstruct_text(doc), "Hallo,Welt")

    def test_punctuation_sentence(self):
        self._roundtrip("Hallo, Welt.")

    def test_emoji_in_gaps(self):
        source = "…emoji…"
        doc, _ = compile_text(source, self.profile)
        self.assertEqual(reconstruct_text(doc), source)

    def test_store_case_false_lowercase(self):
        self._roundtrip("hallo welt", store_case=False)

    def test_explicit_case_preserved(self):
        source = "HaLlo"
        doc, _ = compile_text(source, self.profile)
        self.assertEqual(reconstruct_text(doc), source)

    def test_skipped_digits_only_raises(self):
        with self.assertRaises(ValueError):
            compile_text("123", self.profile)

    def test_gap_symmetry_assertion(self):
        doc, _ = compile_text("Hallo Welt", self.profile)
        assert_gap_symmetry(doc)
        doc.gaps.append("x")
        with self.assertRaises(ValueError):
            assert_gap_symmetry(doc)


if __name__ == "__main__":
    unittest.main()
