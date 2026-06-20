import random
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from gpm.compiler import compile_text
from gpm.hierarchy_geom import TokenSpan, nodes_intersecting
from gpm.interval_index import BITSET_TOKEN_LIMIT, build_interval_index, nodes_intersecting_indexed
from ge_prime.hierarchy import detect_enjambement


class TestIntervalIndex(unittest.TestCase):
    TEXTS = (
        "Hallo, Welt!\nNeue Zeile hier.",
        "Erster Absatz.\n\nZweiter Absatz mit mehr Text.\nNoch eine Zeile.",
        "Kurz. Lang und ausführlich.\nZeile zwei.",
    )

    LEVELS = (
        ("phrase", lambda h: h.semantic.phrases),
        ("sentence", lambda h: h.semantic.sentences),
        ("paragraph", lambda h: h.semantic.paragraphs),
        ("line", lambda h: h.structural.lines),
        ("page", lambda h: h.structural.pages),
    )

    def _assert_parity(self, idx, level, nodes, span):
        legacy = nodes_intersecting(nodes, span)
        indexed = idx.query(level, span)
        self.assertEqual(
            sorted(n.token_start for n in legacy),
            sorted(n.token_start for n in indexed),
            "Segment tree divergence detected!",
        )

    def test_query_matches_linear_scan_random(self):
        rng = random.Random(42)
        for text in self.TEXTS:
            doc, _, _ = compile_text(text)
            h = doc.hierarchy
            idx = build_interval_index(h, len(doc.tokens))
            token_count = len(doc.tokens)
            for level, node_fn in self.LEVELS:
                nodes = node_fn(h)
                for _ in range(20):
                    start = rng.randint(0, max(0, token_count - 1))
                    count = rng.randint(1, max(1, token_count - start))
                    span = TokenSpan(start, count)
                    self._assert_parity(idx, level, nodes, span)

    def test_bitset_enabled_under_limit(self):
        text = "Hallo, Welt!\nNeue Zeile hier."
        doc, _, _ = compile_text(text)
        idx = build_interval_index(doc.hierarchy, len(doc.tokens))
        self.assertLessEqual(len(doc.tokens), BITSET_TOKEN_LIMIT)
        self.assertIsNotNone(idx.sentence._bitmasks)
        self.assertIsNotNone(idx.line._bitmasks)

    def test_bitset_disabled_over_limit(self):
        text = " ".join(f"w{i}" for i in range(5000))
        doc, _, _ = compile_text(text)
        self.assertGreater(len(doc.tokens), BITSET_TOKEN_LIMIT)
        idx = build_interval_index(doc.hierarchy, len(doc.tokens))
        self.assertIsNone(idx.sentence._bitmasks)

    def test_enjambement_parity(self):
        text = "Ein Satz geht\nweiter hier."
        doc, _, _ = compile_text(text)
        h = doc.hierarchy
        idx = build_interval_index(h, len(doc.tokens))
        baseline = detect_enjambement(h.semantic.sentences, h.structural.lines)
        indexed = detect_enjambement(
            h.semantic.sentences, h.structural.lines, interval_index=idx
        )
        self.assertEqual(baseline["enjambement_profile"], indexed["enjambement_profile"])
        self.assertEqual(baseline["rhythm_break_count"], indexed["rhythm_break_count"])


if __name__ == "__main__":
    unittest.main()
