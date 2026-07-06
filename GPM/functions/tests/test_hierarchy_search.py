import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from alphabets import AlphabetProfile
from analysis.compile.compiler import compile_text
from analysis.search.hierarchy_search import hierarchy_search
from analysis.substance.compare import substance_covers


class TestHierarchySearch(unittest.TestCase):
    def test_kgv_pruning_direction(self):
        local = 12
        target = 6
        self.assertTrue(substance_covers(local, target))
        self.assertFalse(substance_covers(6, 12))

    def test_hierarchy_search_paragraph(self):
        text = "Absatz eins. Noch ein Satz.\n\nZweiter Absatz."
        pattern = "Absatz eins."
        doc, _ = compile_text(text, AlphabetProfile.OG)
        result = hierarchy_search(doc, pattern_text=pattern, level="paragraph")
        self.assertIn("matches", result)
        self.assertIn("s_target", result)

    def test_line_aligned_query(self):
        text = "a = 1\nb = 2"
        doc, _ = compile_text(text, AlphabetProfile.OG)
        result = hierarchy_search(doc, pattern_text="a", query="line_aligned")
        self.assertEqual(result["query"], "line_aligned")
        self.assertIn("cross_analysis", result)


if __name__ == "__main__":
    unittest.main()
