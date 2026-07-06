"""F6 — algebra/__init__.py Export-Vollständigkeit."""

import unittest

import analysis.algebra as algebra


class TestAlgebraPackageExports(unittest.TestCase):
    def test_critical_exports_importable(self):
        for name in (
            "compare_substances",
            "substance_covers",
            "exponent_window_to_substance",
            "log_jaccard_basis_blend",
            "counter_overlap",
            "empty_transition_fields",
        ):
            self.assertTrue(hasattr(algebra, name), f"missing export: {name}")
            self.assertIn(name, algebra.__all__)

    def test_all_names_importable(self):
        for name in algebra.__all__:
            self.assertTrue(hasattr(algebra, name), f"__all__ entry not found: {name}")


if __name__ == "__main__":
    unittest.main()
