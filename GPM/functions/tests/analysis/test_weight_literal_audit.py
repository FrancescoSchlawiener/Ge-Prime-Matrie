"""Härtungs-Invariante F-B — keine Inline-Gewichts-Literale in Blend-Ausdrücken."""

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "analysis"

FORBIDDEN_FILES = [
    ROOT / "algebra" / "window_fold.py",
    ROOT / "basis" / "compare_tiered.py",
    ROOT / "meta" / "compare.py",
]

FORBIDDEN_LITERALS = {0.67, 0.33, 0.5, 0.3, 0.2, 0.6, 0.95, 0.05, 0.25, 0.15, 0.20}


class TestWeightLiteralAudit(unittest.TestCase):
    def _blend_literals(self, path: Path) -> set[float]:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        found: set[float] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Mult, ast.Add)):
                for child in ast.walk(node):
                    if isinstance(child, ast.Constant) and isinstance(child.value, float):
                        if child.value in FORBIDDEN_LITERALS:
                            found.add(child.value)
        return found

    def test_no_forbidden_weight_literals(self):
        for path in FORBIDDEN_FILES:
            found = self._blend_literals(path)
            self.assertEqual(
                found,
                set(),
                f"{path.name} contains forbidden blend weight literals: {found}",
            )


if __name__ == "__main__":
    unittest.main()
