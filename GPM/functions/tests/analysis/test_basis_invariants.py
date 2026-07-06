"""Tests für Basis-Invarianten A (Profil-Guard) und B (log_norm ohne profile_to_vector)."""

import math
import unittest
from collections import Counter
from unittest.mock import patch

from alphabets import AlphabetProfile
from analysis.algebra.gates import profile_symmetry_guard, substance_pair_gate
from analysis.algebra.log_profile import profile_log_norm
from analysis.basis.compare_tiered import CompareTier, compare_documents_tiered
from analysis.basis.index import build_basis_index, query_candidates
from analysis.basis.scoring import basis_score_from_components
from analysis.basis.signature import build_basis_signature, get_basis_signature
from analysis.compile.compiler import compile_text


class TestBasisInvariants(unittest.TestCase):
    def test_profile_mismatch_guard(self):
        ok, reason = profile_symmetry_guard(AlphabetProfile.PHOENICIAN, AlphabetProfile.CYRILLIC)
        self.assertFalse(ok)
        self.assertEqual(reason, "profile_mismatch")

    def test_substance_pair_gate_rejects_cross_profile(self):
        ok, reason = substance_pair_gate(
            100,
            200,
            profile_a=AlphabetProfile.OG,
            profile_b=AlphabetProfile.GREEK,
        )
        self.assertFalse(ok)
        self.assertEqual(reason, "profile_mismatch")

    def test_compare_tiered_profile_mismatch(self):
        doc_a, _ = compile_text("ABC", AlphabetProfile.OG)
        doc_b, _ = compile_text("АБВ", AlphabetProfile.CYRILLIC)
        result = compare_documents_tiered(doc_a, doc_b, max_tier=CompareTier.FULL)
        self.assertEqual(result.zero_reason, "profile_mismatch")
        self.assertEqual(result.stopped_at, CompareTier.GATE)

    def test_query_candidates_cross_profile_certificate(self):
        doc_a, _ = compile_text("ABC", AlphabetProfile.OG)
        doc_b, _ = compile_text("αβγ", AlphabetProfile.GREEK)
        partitions = build_basis_index([("a", doc_a), ("b", doc_b)])
        sig_a = get_basis_signature(doc_a, doc_id="a")
        wrong_index = partitions[AlphabetProfile.GREEK]
        result = query_candidates(wrong_index, sig_a)
        self.assertEqual(result.zero_reason, "profile_mismatch")
        self.assertEqual(result.candidates, [])

    def test_weight_renorm_without_relation_sketch(self):
        with_sketch = basis_score_from_components(0.8, 0.6, 0.4, has_relation_sketch=True)
        without = basis_score_from_components(0.8, 0.6, 0.4, has_relation_sketch=False)
        self.assertAlmostEqual(without, 0.67 * 0.8 + 0.33 * 0.6)
        self.assertGreater(without, 0.6 * 0.8 + 0.3 * 0.6)

    def test_profile_log_norm_o_k(self):
        profile = Counter({2: 3, 3: 1, 5: 2})
        expected = sum(exp * math.log(p) for p, exp in profile.items())
        self.assertAlmostEqual(profile_log_norm(profile), expected)

    @patch("analysis.meta.fingerprint.profile_to_vector")
    def test_build_basis_signature_never_calls_profile_to_vector(self, mock_vector):
        mock_vector.side_effect = AssertionError("profile_to_vector must not be used for log_norm")
        doc, _ = compile_text("Hallo Welt.", AlphabetProfile.OG)
        sig = build_basis_signature(doc)
        self.assertGreater(sig.log_norm, 0.0)
        mock_vector.assert_not_called()

    def test_doc_id_cache_rebuilds_on_change(self):
        doc, _ = compile_text("Test", AlphabetProfile.OG)
        sig1 = get_basis_signature(doc, doc_id="first")
        sig2 = get_basis_signature(doc, doc_id="second")
        self.assertEqual(sig1.doc_id, "first")
        self.assertEqual(sig2.doc_id, "second")


if __name__ == "__main__":
    unittest.main()
