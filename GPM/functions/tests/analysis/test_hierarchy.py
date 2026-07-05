"""Tests für Hierarchie-Geometrie."""

import unittest

from alphabets import AlphabetProfile
from analysis.blocks.build import materialize_geometry
from analysis.compile.compiler import compile_text
from analysis.hierarchy.geom import build_document_hierarchy, validate_structural_partition
from analysis.index.interval_index import build_interval_index
from analysis.blocks.node import TokenSpan


class TestHierarchy(unittest.TestCase):
    def test_build_hierarchy_hallo_welt(self):
        doc, _ = compile_text("Hallo Welt.", AlphabetProfile.OG)
        hier = build_document_hierarchy(doc)
        self.assertGreater(len(hier.semantic.sentences), 0)
        validate_structural_partition(len(doc.tokens), hier.structural.lines)

    def test_interval_index_query(self):
        doc, _ = compile_text("Hallo Welt. Noch ein Satz.", AlphabetProfile.OG)
        materialize_geometry(doc)
        idx = build_interval_index(doc.hierarchy, len(doc.tokens))
        hits = idx.query("sentence", TokenSpan(0, len(doc.tokens)))
        self.assertGreater(len(hits), 0)


if __name__ == "__main__":
    unittest.main()
