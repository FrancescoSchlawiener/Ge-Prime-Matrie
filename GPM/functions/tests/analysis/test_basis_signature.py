"""Tests für BasisSignature."""

import unittest

from alphabets import AlphabetProfile
from analysis.basis.signature import build_basis_signature, get_basis_signature
from analysis.compile.compiler import compile_text
from analysis.profile.prime_profile import build_prime_profile


class TestBasisSignature(unittest.TestCase):
    def test_non_og_profile(self):
        doc, _ = compile_text("αβγ", AlphabetProfile.GREEK)
        sig = build_basis_signature(doc)
        self.assertEqual(sig.profile, AlphabetProfile.GREEK)
        self.assertEqual(sig.prime_profile, build_prime_profile(doc))

    def test_lazy_cache(self):
        doc, _ = compile_text("Test", AlphabetProfile.OG)
        sig1 = get_basis_signature(doc, doc_id="t1")
        sig2 = get_basis_signature(doc, doc_id="t1")
        self.assertIs(sig1, sig2)

    def test_log_norm_positive(self):
        doc, _ = compile_text("Hallo Welt.", AlphabetProfile.OG)
        sig = build_basis_signature(doc)
        self.assertGreater(sig.log_norm, 0.0)


if __name__ == "__main__":
    unittest.main()
