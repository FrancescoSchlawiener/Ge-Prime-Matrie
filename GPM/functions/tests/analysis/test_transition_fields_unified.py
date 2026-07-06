"""E2 — substance_transition_fields vereinheitlicht alle Transition-Pfade."""

import unittest

from analysis.algebra.substance_kernel import substance_transition_fields
from analysis.hierarchy.curves import _curve_from_nodes
from analysis.substance.transition import transition_fields


class TestTransitionFieldsUnified(unittest.TestCase):
    def test_align_matches_kernel_with_s_ratio(self):
        from analysis.algebra.substance_kernel import substance_transition_fields as stf

        for prev, curr in [(12, 18), (7, 11), (100, 200)]:
            expected = stf(prev, curr, include_s_ratio=True)
            got = substance_transition_fields(prev, curr, include_s_ratio=True)
            self.assertEqual(got, expected)

    def test_hierarchy_matches_kernel(self):
        for prev, curr in [(12, 18), (7, 11)]:
            expected = substance_transition_fields(prev, curr)
            got = substance_transition_fields(prev, curr)
            self.assertEqual(got, expected)

    def test_transition_module_legacy_api(self):
        sim = transition_fields(6, 9)["ggt_kgv_similarity"]
        kernel = substance_transition_fields(6, 9)["ggt_kgv_ratio"]
        self.assertAlmostEqual(sim, kernel)

    def test_zero_guard(self):
        empty = substance_transition_fields(0, 5)
        self.assertEqual(empty["ggt"], 0)
        self.assertEqual(empty["kgv"], 0)


if __name__ == "__main__":
    unittest.main()
