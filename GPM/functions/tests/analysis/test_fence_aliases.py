"""Fence-Language-Aliases."""

import unittest

from analysis.code.context import scan_fences_hybrid
from analysis.code.languages import resolve_fence_language


class TestFenceAliases(unittest.TestCase):
    def test_resolve_javascript(self):
        self.assertEqual(resolve_fence_language("javascript"), "js")

    def test_resolve_python3(self):
        self.assertEqual(resolve_fence_language("python3"), "py")

    def test_scan_hybrid_javascript_fence(self):
        src = "```javascript\nconst x = 1;\n```\n"
        segs = scan_fences_hybrid(src)
        code = [s for s in segs if s.language_id is not None]
        self.assertEqual(len(code), 1)
        self.assertEqual(code[0].language_id, "js")


if __name__ == "__main__":
    unittest.main()
