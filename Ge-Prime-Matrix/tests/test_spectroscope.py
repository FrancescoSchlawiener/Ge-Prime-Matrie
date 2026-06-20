import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ge_prime.spectroscope import spectroscope_analyze, spectroscope_from_text
from gpm.compiler import compile_text
from pipeline.normalize import normalize_text_nfc


class TestSpectroscope(unittest.TestCase):
    def test_crossfire_separate_scores(self):
        text = "Hallo Welt. Das ist ein Test.\nZweite Zeile hier."
        doc, _, _ = compile_text(text)
        result = spectroscope_analyze(
            doc,
            token_start=0,
            token_end=2,
            modes=["structural_twin"],
        )
        for match in result["matches"]:
            layer = match.get("layer")
            if layer == "semantic":
                self.assertIn("score_semantic", match)
            if layer == "structural":
                self.assertIn("score_structural", match)

    def test_spectroscope_from_text_selection(self):
        text = "Alpha Beta Gamma."
        result = spectroscope_from_text(text, selection_start=0, selection_end=5, modes=["anagram_shadow"])
        self.assertIn("target", result)
        self.assertIn("matches", result)
        self.assertIn("token_char_map", result)

    def test_spectroscope_nfd_selection_after_nfc_wash(self):
        nfd = "Gr\u0061\u0308ser wachsen."
        nfc = normalize_text_nfc(nfd)
        result = spectroscope_from_text(
            nfd,
            selection_start=0,
            selection_end=len(nfc),
            modes=["substance_divisor"],
        )
        self.assertGreaterEqual(result["target"]["token_end"], result["target"]["token_start"])

    def test_structural_twin_skips_dtw_when_kgv_gate_fails(self):
        from unittest.mock import patch

        text = "Alpha beta gamma. Delta epsilon zeta."
        doc, _, _ = compile_text(text)
        with patch("ge_prime.spectroscope.compare_level_sequences") as mock_cmp:
            mock_cmp.return_value = {"geometry_score": 0.99}
            with patch("ge_prime.spectroscope.passes_kgv_gate", return_value=False):
                result = spectroscope_analyze(
                    doc,
                    token_start=0,
                    token_end=2,
                    modes=["structural_twin"],
                )
            mock_cmp.assert_not_called()
            self.assertEqual(result["match_count"], 0)

    def test_structural_twin_queries_interval_index_before_dtw(self):
        from unittest.mock import patch

        from ge_prime.hierarchy import get_interval_index
        from gpm.hierarchy_geom import TokenSpan

        text = "Alpha beta gamma. Delta epsilon zeta.\nAnother line here."
        doc, _, _ = compile_text(text)
        idx = get_interval_index(doc)
        with patch.object(idx, "query", wraps=idx.query) as mock_query:
            with patch("ge_prime.spectroscope.get_interval_index", return_value=idx):
                with patch(
                    "ge_prime.spectroscope.compare_level_sequences",
                    return_value={"geometry_score": 0.0},
                ):
                    spectroscope_analyze(
                        doc,
                        token_start=0,
                        token_end=2,
                        modes=["structural_twin"],
                    )
        doc_span = TokenSpan(0, max(1, len(doc.tokens)))
        mock_query.assert_any_call("sentence", doc_span)
        mock_query.assert_any_call("line", doc_span)

    def test_structural_twin_empty_tokens_uses_doc_span_guard(self):
        from unittest.mock import patch

        from ge_prime.hierarchy import get_interval_index
        from gpm.hierarchy_geom import TokenSpan
        from gpm.model import GpmDocument

        doc = GpmDocument(tokens=[])
        idx = get_interval_index(doc)
        with patch.object(idx, "query", wraps=idx.query) as mock_query:
            with patch("ge_prime.spectroscope.get_interval_index", return_value=idx):
                with patch("ge_prime.spectroscope.get_hierarchy"):
                    with patch("ge_prime.spectroscope.nodes_for_token_span", return_value={"sentences": [], "lines": []}):
                        with patch("ge_prime.spectroscope.get_substance_index"):
                            with patch("ge_prime.spectroscope.window_fingerprint"):
                                result = spectroscope_analyze(
                                    doc,
                                    token_start=0,
                                    token_end=0,
                                    modes=["structural_twin"],
                                )
        doc_span = TokenSpan(0, 1)
        mock_query.assert_any_call("sentence", doc_span)
        mock_query.assert_any_call("line", doc_span)
        self.assertEqual(result["match_count"], 0)

    def test_merge_interval_collision(self):
        """Dual char interval → crossfire className (Gesetz 2 logic)."""
        matches = [
            {
                "char_start": 0,
                "char_end": 5,
                "layer": "semantic",
                "mode": "structural_twin",
                "score_semantic": 0.9,
            },
            {
                "char_start": 0,
                "char_end": 5,
                "layer": "structural",
                "mode": "structural_twin",
                "score_structural": 0.85,
            },
        ]
        sorted_m = sorted(matches, key=lambda a: (a["char_start"], -a["char_end"]))
        merged = []
        for match in sorted_m:
            existing = next(
                (m for m in merged if m["char_start"] == match["char_start"] and m["char_end"] == match["char_end"]),
                None,
            )
            if existing and existing["layer"] != match["layer"]:
                existing["className"] = "spectro-crossfire"
            elif not existing:
                match["className"] = "spectro-teal"
                merged.append(match)
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["className"], "spectro-crossfire")


if __name__ == "__main__":
    unittest.main()
