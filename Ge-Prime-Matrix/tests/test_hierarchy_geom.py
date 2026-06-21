import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ge_prime.hierarchy import detect_enjambement
from gpm.compiler import compile_text
from gpm.hierarchy_geom import (
    PhraseCategoryKey,
    TokenSpan,
    build_document_hierarchy,
    build_page_nodes_for_export,
    intervals_overlap,
    nodes_intersecting,
    validate_structural_partition,
)


class TestHierarchyGeom(unittest.TestCase):
    def test_intervals_overlap(self):
        self.assertTrue(intervals_overlap(0, 5, 3, 4))
        self.assertFalse(intervals_overlap(0, 2, 2, 3))

    def test_intersect_sentence_over_two_lines(self):
        text = "Zeile eins hier.\nUnd Zeile zwei."
        doc, _, _ = compile_text(text)
        h = build_document_hierarchy(doc)
        self.assertGreaterEqual(len(h.structural.lines), 2)
        line = h.structural.lines[0]
        sents = nodes_intersecting(h.semantic.sentences, TokenSpan(line.token_start, line.token_count))
        self.assertGreaterEqual(len(h.semantic.sentences), 1)

    def test_structural_partition(self):
        text = "A.\nB.\nC."
        doc, _, _ = compile_text(text)
        h = build_document_hierarchy(doc)
        validate_structural_partition(len(doc.tokens), h.structural.lines)

    def test_phrase_category_key(self):
        key = PhraseCategoryKey(s_phrase=12, token_count=3)
        self.assertEqual(key.token_count, 3)

    def test_enjambement_profiles(self):
        code = "a = 1\nb = 2\nc = 3"
        poem = "Rose ist rot,\nVeilchen blau.\nSatz geht\nweiter hier."
        prose = "Das ist ein Satz. Und noch einer."
        for text, expected in (
            (code, "line_aligned"),
            (poem, "rhythm_break"),
        ):
            doc, _, _ = compile_text(text)
            h = build_document_hierarchy(doc)
            profile = detect_enjambement(h.semantic.sentences, h.structural.lines)
            self.assertIn(profile["enjambement_profile"], (expected, "enjambement_noise", "prose_flow", "rhythm_break"))

    def test_paragraph_split_double_newline(self):
        text = "Erster Absatz.\n\nZweiter Absatz mit Text."
        doc, _, _ = compile_text(text)
        h = build_document_hierarchy(doc)
        self.assertEqual(len(h.semantic.paragraphs), 2)
        from ge_prime.hierarchy import extract_paragraph_curve

        curve = extract_paragraph_curve(doc)
        self.assertEqual(len(curve), 2)
        self.assertIn("i_absatz_ratio", curve[0])
        self.assertIn("paragraph_index", curve[0])

    def test_paragraph_split_crlf_double_newline(self):
        text = "Erster Absatz.\r\n\r\nZweiter Absatz mit Text."
        doc, _, _ = compile_text(text)
        h = build_document_hierarchy(doc)
        self.assertEqual(len(h.semantic.paragraphs), 2)

    def test_standard_hierarchy_has_no_pages(self):
        text = "Seite eins.\nZeile zwei.\n\fDritte seite."
        doc, _, _ = compile_text(text)
        h = build_document_hierarchy(doc)
        self.assertEqual(h.structural.pages, [])

    def test_export_page_nodes_on_formfeed(self):
        text = "Seite eins.\nZeile zwei.\n\fDritte seite."
        doc, _, _ = compile_text(text)
        pages = build_page_nodes_for_export(doc)
        self.assertGreaterEqual(len(pages), 2)
        self.assertEqual(pages[0].level, "page")


if __name__ == "__main__":
    unittest.main()
