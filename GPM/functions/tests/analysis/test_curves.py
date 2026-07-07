"""Tests für Kurven (I-Kurve, Substanz-Kette)."""

import unittest

from alphabets import AlphabetProfile
from analysis.blocks.build import materialize_geometry
from analysis.compile.compiler import compile_text
from analysis.curves.i_curve import extract_cell_curve, extract_i_curve
from analysis.document.model import GpmToken
from analysis.document.preview import assert_referential_integrity
from analysis.curves.substance_curve import extract_substance_curve
from gpm_types.classify import PayloadKind
from analysis.index.substance_index import build_substance_index, window_fingerprint


class TestCurves(unittest.TestCase):
    def test_token_i_curve(self):
        doc, _ = compile_text("Hallo Welt", AlphabetProfile.OG)
        curve = extract_i_curve(doc)
        self.assertEqual(len(curve), len(doc.tokens))

    def test_cell_i_curve(self):
        doc, _ = compile_text("Hallo Welt.", AlphabetProfile.OG)
        materialize_geometry(doc)
        curve = extract_cell_curve(doc)
        self.assertGreater(len(curve), 0)
        self.assertTrue(all(row.get("label") for row in curve))

    def test_assert_referential_integrity_rejects_bad_word_id(self):
        doc, _ = compile_text("A", AlphabetProfile.OG)
        doc.tokens[0] = GpmToken(
            word_id=99,
            perm_index=doc.tokens[0].perm_index,
            case_code=doc.tokens[0].case_code,
            payload_kind=PayloadKind.S,
        )
        with self.assertRaises(ValueError):
            assert_referential_integrity(doc)

    def test_substance_index_window(self):
        doc, _ = compile_text("LISTEN SILENT", AlphabetProfile.OG)
        idx = build_substance_index(doc)
        fp = window_fingerprint(idx, 0, len(doc.tokens))
        self.assertGreater(len(fp.exponents), 0)

    def test_substance_curve(self):
        doc, _ = compile_text("Hallo Welt", AlphabetProfile.OG)
        chain = extract_substance_curve(doc)
        self.assertEqual(len(chain), len(doc.tokens))


if __name__ == "__main__":
    unittest.main()
