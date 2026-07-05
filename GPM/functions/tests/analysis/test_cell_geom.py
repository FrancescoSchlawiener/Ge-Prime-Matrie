"""Tests für Zell-Geometrie."""

import unittest

from alphabets import AlphabetProfile
from analysis.blocks.build import materialize_geometry
from analysis.cell.geom import build_document_cells, cells_cover_document
from analysis.compile.compiler import compile_text


class TestCellGeom(unittest.TestCase):
    def test_cells_cover_document(self):
        doc, _ = compile_text("Hallo Welt.", AlphabetProfile.OG)
        cells = build_document_cells(doc)
        self.assertTrue(cells_cover_document(doc, cells))

    def test_materialize_populates_cells(self):
        doc, _ = compile_text("Alpha Beta Gamma.", AlphabetProfile.OG)
        materialize_geometry(doc)
        self.assertIsNotNone(doc.cells)
        self.assertTrue(len(doc.cells) > 0)


if __name__ == "__main__":
    unittest.main()
