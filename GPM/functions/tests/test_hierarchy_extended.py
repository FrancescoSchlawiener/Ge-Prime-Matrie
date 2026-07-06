"""Tests für erweiterte Hierarchie-Funktionen."""

import unittest

from alphabets import AlphabetProfile
from analysis.blocks.build import materialize_geometry
from analysis.compile.compiler import compile_text
from analysis.hierarchy.access import get_hierarchy, get_interval_index
from analysis.hierarchy.compare import compare_level_sequences
from analysis.hierarchy.curves import (
    extract_line_curve,
    extract_page_curve,
    extract_paragraph_curve,
    extract_sentence_curve,
)
from analysis.hierarchy.enjambement import cross_analysis, detect_enjambement
from analysis.hierarchy.span_utils import (
    char_range_for_tokens,
    nodes_for_document_span,
    token_char_map,
)


class TestHierarchyExtended(unittest.TestCase):
    MULTILINE = "Erste Zeile hier.\nZweite Zeile\nund ein dritter Satz."

    def test_extract_curves_have_ratio_keys(self):
        doc, _ = compile_text(self.MULTILINE, AlphabetProfile.OG)
        materialize_geometry(doc)
        line_curve = extract_line_curve(doc)
        sent_curve = extract_sentence_curve(doc)
        para_curve = extract_paragraph_curve(doc)
        page_curve = extract_page_curve(doc)
        if line_curve:
            self.assertIn("i_zeile_ratio", line_curve[0])
            self.assertIn("line_index", line_curve[0])
            self.assertIn("text", line_curve[0])
            self.assertTrue(line_curve[0]["text"])
        if sent_curve:
            self.assertIn("i_satz_ratio", sent_curve[0])
            self.assertIn("text", sent_curve[0])
            self.assertTrue(sent_curve[0]["text"])
        if para_curve:
            self.assertIn("i_absatz_ratio", para_curve[0])
            self.assertIn("text", para_curve[0])
            self.assertTrue(para_curve[0]["text"])
        self.assertIsInstance(page_curve, list)

    def test_compare_level_sequences(self):
        doc_a, _ = compile_text("Hallo Welt.", AlphabetProfile.OG)
        doc_b, _ = compile_text("Hallo Welt.", AlphabetProfile.OG)
        materialize_geometry(doc_a)
        materialize_geometry(doc_b)
        seq_a = extract_sentence_curve(doc_a)
        seq_b = extract_sentence_curve(doc_b)
        cmp = compare_level_sequences(seq_a, seq_b, ratio_key="i_satz_ratio")
        self.assertEqual(cmp["method"], "dtw")
        self.assertGreaterEqual(cmp["geometry_score"], 0.0)

    def test_enjambement_multiline(self):
        doc, _ = compile_text(self.MULTILINE, AlphabetProfile.OG)
        materialize_geometry(doc)
        cross = cross_analysis(doc)
        self.assertIn("enjambement_profile", cross)
        self.assertIn(cross["enjambement_profile"], (
            "line_aligned",
            "enjambement_noise",
            "rhythm_break",
            "prose_flow",
        ))

    def test_detect_enjambement_direct(self):
        doc, _ = compile_text("A\nB\nC", AlphabetProfile.OG)
        materialize_geometry(doc)
        h = get_hierarchy(doc)
        result = detect_enjambement(h.semantic.sentences, h.structural.lines)
        self.assertIn("rhythm_break_count", result)

    def test_token_char_map(self):
        doc, _ = compile_text("Hallo Welt", AlphabetProfile.OG)
        mapping = token_char_map(doc)
        self.assertEqual(len(mapping), len(doc.tokens))
        start, end = char_range_for_tokens(doc, 0, len(doc.tokens))
        self.assertLess(start, end)

    def test_nodes_for_document_span(self):
        doc, _ = compile_text(self.MULTILINE, AlphabetProfile.OG)
        materialize_geometry(doc)
        nodes = nodes_for_document_span(doc, 0, len(doc.tokens))
        self.assertIn("sentences", nodes)
        self.assertIn("lines", nodes)

    def test_hierarchy_built_once(self):
        from unittest.mock import patch

        from analysis.hierarchy.geom import build_document_hierarchy

        doc, _ = compile_text("One two three. Four five six.", AlphabetProfile.OG)
        doc.hierarchy = None
        doc.interval_index = None
        calls = 0
        original = build_document_hierarchy

        def counting(document):
            nonlocal calls
            calls += 1
            return original(document)

        with patch("analysis.hierarchy.access.build_document_hierarchy", side_effect=counting):
            get_hierarchy(doc)
            get_hierarchy(doc)
            get_interval_index(doc)
        self.assertEqual(calls, 1)


if __name__ == "__main__":
    unittest.main()
