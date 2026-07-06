"""E6 — domain_scalar_gate ohne DB."""

import unittest

from analysis.algebra.gates import domain_scalar_gate


class TestDomainScalarGate(unittest.TestCase):
    def test_passes_both_thresholds(self):
        ok, reason = domain_scalar_gate(0.5, 0.5)
        self.assertTrue(ok)
        self.assertIsNone(reason)

    def test_fails_low_overlap(self):
        ok, reason = domain_scalar_gate(0.1, 0.5)
        self.assertFalse(ok)
        self.assertEqual(reason, "profile_overlap_low")

    def test_fails_low_relation(self):
        ok, reason = domain_scalar_gate(0.5, 0.1)
        self.assertFalse(ok)
        self.assertEqual(reason, "relation_score_low")


if __name__ == "__main__":
    unittest.main()
