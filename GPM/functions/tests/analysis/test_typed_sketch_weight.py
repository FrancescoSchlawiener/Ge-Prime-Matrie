"""Härtungs-Invariante E-C — typed_sketch default weight 0.0."""

import unittest

from alphabets import AlphabetProfile
from analysis.basis.compare_tiered import CompareTier, compare_documents_tiered
from analysis.basis.scoring import basis_score_from_components
from analysis.basis.signature import build_basis_signature
from analysis.compile.compiler import compile_text


class TestTypedSketchWeight(unittest.TestCase):
    def test_basis_score_unchanged_without_fusion_mode(self):
        base = basis_score_from_components(
            0.8, 0.6, 0.4, has_relation_sketch=False, typed_sketch=0.99
        )
        without = basis_score_from_components(
            0.8, 0.6, 0.4, has_relation_sketch=False, typed_sketch=0.0
        )
        self.assertAlmostEqual(base, without)

    def test_fusion_mode_typed_applies_weight(self):
        base = basis_score_from_components(
            0.8, 0.6, 0.4, has_relation_sketch=False, typed_sketch=0.0
        )
        fused = basis_score_from_components(
            0.8,
            0.6,
            0.4,
            has_relation_sketch=False,
            typed_sketch=1.0,
            fusion_mode="typed",
            typed_weight=0.1,
        )
        self.assertGreater(fused, base)

    def test_document_compare_default_path(self):
        doc_a, _ = compile_text("Hallo Welt.", AlphabetProfile.OG)
        doc_b, _ = compile_text("Welt Hallo.", AlphabetProfile.OG)
        sig_a = build_basis_signature(doc_a, include_typed_sketch=True)
        sig_b = build_basis_signature(doc_b, include_typed_sketch=True)
        result_default = compare_documents_tiered(
            doc_a, doc_b, max_tier=CompareTier.BASIS, sig_a=sig_a, sig_b=sig_b
        )
        sig_a2 = build_basis_signature(doc_a, include_typed_sketch=False)
        sig_b2 = build_basis_signature(doc_b, include_typed_sketch=False)
        result_no_sketch = compare_documents_tiered(
            doc_a, doc_b, max_tier=CompareTier.BASIS, sig_a=sig_a2, sig_b=sig_b2
        )
        self.assertAlmostEqual(result_default.basis_score, result_no_sketch.basis_score)


if __name__ == "__main__":
    unittest.main()
