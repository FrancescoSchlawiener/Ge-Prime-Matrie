"""Tests für analysis/algebra/gates.py."""

import unittest
from collections import Counter

from alphabets import AlphabetProfile
from analysis.algebra.gates import (
    passes_document_relevance,
    prime_sets_disjoint,
    profile_pair_gate,
    substance_pair_gate,
)
from analysis.basis.signature import build_basis_signature
from analysis.compile.compiler import compile_text


class TestAlgebraGates(unittest.TestCase):
    def test_gcd_le_1(self):
        ok, reason = substance_pair_gate(
            2,
            3,
            profile_a=AlphabetProfile.OG,
            profile_b=AlphabetProfile.OG,
        )
        self.assertFalse(ok)
        self.assertEqual(reason, "gcd_le_1")

    def test_prime_sets_disjoint(self):
        self.assertTrue(prime_sets_disjoint(Counter({2: 1}), Counter({3: 1})))
        self.assertFalse(prime_sets_disjoint(Counter({2: 1}), Counter({2: 2})))

    def test_profile_pair_gate_empty(self):
        ok, reason = profile_pair_gate(
            Counter(),
            Counter({2: 1}),
            doc_profile_a=AlphabetProfile.OG,
            doc_profile_b=AlphabetProfile.OG,
        )
        self.assertFalse(ok)
        self.assertEqual(reason, "empty_profile_a")

    def test_passes_document_relevance(self):
        doc_a, _ = compile_text("Hallo", AlphabetProfile.OG)
        doc_b, _ = compile_text("Welt", AlphabetProfile.OG)
        sig_a = build_basis_signature(doc_a)
        sig_b = build_basis_signature(doc_b)
        gate = passes_document_relevance(sig_a, sig_b)
        self.assertTrue(gate.passed or gate.zero_reason in ("log_similarity_zero", "no_shared_primes"))


if __name__ == "__main__":
    unittest.main()
