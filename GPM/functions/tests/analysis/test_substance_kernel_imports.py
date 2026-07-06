"""F-1 — Produktionscode importiert Substanz-Kernel über analysis.algebra.substance_kernel."""

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "analysis"

F1_TARGETS = [
    ROOT / "align" / "substance_align.py",
    ROOT / "hierarchy" / "curves.py",
    ROOT / "search" / "hierarchy_search.py",
    ROOT / "curves" / "compare.py",
    ROOT / "substance" / "transition.py",
    ROOT / "algebra" / "fold.py",
    ROOT / "algebra" / "multiset.py",
    ROOT / "binary" / "search.py",
    ROOT / "pair" / "analyze_word_pair.py",
]


class TestSubstanceKernelImports(unittest.TestCase):
    def test_f1_modules_use_substance_kernel(self):
        for path in F1_TARGETS:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            imports = [
                node
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.module
            ]
            kernel_imports = [
                n for n in imports if n.module and "substance_kernel" in n.module
            ]
            legacy_compare = [
                n for n in imports if n.module == "analysis.substance.compare"
            ]
            self.assertTrue(
                kernel_imports,
                f"{path.name} should import from analysis.algebra.substance_kernel",
            )
            if path.name not in ("transition.py",):
                self.assertFalse(
                    legacy_compare,
                    f"{path.name} should not import analysis.substance.compare directly",
                )


if __name__ == "__main__":
    unittest.main()
