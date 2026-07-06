"""Tests für compare_documents_tiered."""

import unittest

from alphabets import AlphabetProfile
from analysis.basis.compare_tiered import CompareTier, compare_documents_tiered
from analysis.blocks.build import materialize_geometry
from analysis.compile.compiler import compile_text
from analysis.curves.compare import analyze_pair


class TestCompareTiered(unittest.TestCase):
    def test_stops_before_full_by_default(self):
        doc_a, _ = compile_text("Hallo Welt.", AlphabetProfile.OG)
        doc_b, _ = compile_text("Welt Hallo.", AlphabetProfile.OG)
        result = compare_documents_tiered(doc_a, doc_b, max_tier=CompareTier.BASIS)
        self.assertEqual(result.stopped_at, CompareTier.BASIS)
        self.assertNotIn("analyze_pair_full", result.tiers_run)

    def test_structure_score_uses_shared_primes(self):
        doc_a, _ = compile_text("Hallo Welt.", AlphabetProfile.OG)
        doc_b, _ = compile_text("Hallo Welt.", AlphabetProfile.OG)
        materialize_geometry(doc_a)
        materialize_geometry(doc_b)
        result = compare_documents_tiered(doc_a, doc_b, max_tier=CompareTier.STRUCTURE)
        self.assertGreater(result.structure_score, 0.0)

    def test_tier4_runs_full(self):
        doc_a, _ = compile_text("Hallo Welt.", AlphabetProfile.OG)
        doc_b, _ = compile_text("Hallo Welt.", AlphabetProfile.OG)
        materialize_geometry(doc_a)
        materialize_geometry(doc_b)
        result = compare_documents_tiered(doc_a, doc_b, max_tier=CompareTier.FULL)
        self.assertEqual(result.stopped_at, CompareTier.FULL)
        self.assertIn("analyze_pair_full", result.tiers_run)

    def test_analyze_pair_basis_prefilter(self):
        doc_a, _ = compile_text("ABC", AlphabetProfile.OG)
        doc_b, _ = compile_text("АБВ", AlphabetProfile.CYRILLIC)
        out = analyze_pair(doc_a, doc_b, basis_prefilter=True)
        self.assertEqual(out.get("zero_reason"), "profile_mismatch")

    def test_prefilter_structure_score_none_in_validation(self):
        from analysis.validation.structure import pair_relevance_prefilter

        doc_a, _ = compile_text("Hallo.", AlphabetProfile.OG)
        doc_b, _ = compile_text("Welt.", AlphabetProfile.OG)
        pre = pair_relevance_prefilter(doc_a, doc_b)
        self.assertIsNone(pre["structure_score"])


if __name__ == "__main__":
    unittest.main()
