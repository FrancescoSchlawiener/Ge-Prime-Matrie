import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class TestGeometricEditorStatic(unittest.TestCase):
    def test_geometric_viewport_read_only(self):
        root = Path(__file__).resolve().parent.parent
        js = (root / "web" / "static" / "geometric_editor.js").read_text(encoding="utf-8")
        html = (root / "web" / "templates" / "index.html").read_text(encoding="utf-8")
        app_js = (root / "web" / "static" / "app.js").read_text(encoding="utf-8")
        css = (root / "web" / "static" / "style.css").read_text(encoding="utf-8")

        self.assertIn("GeometricViewport", js)
        self.assertIn("GeometricMatrix", js)
        self.assertIn("closest", js)
        self.assertIn(".geo-cell", js)
        self.assertIn("data-token-index", js)
        self.assertIn("Read-Only", js)
        self.assertNotIn("contentEditable", js)
        self.assertIn("gpm-geometric-viewport", html)
        self.assertIn("ikurve-geometric-matrix-a", html)
        self.assertNotIn("ikurve-text-a", html)
        self.assertNotIn("ikurve-geometric-viewport-a", html)
        self.assertNotIn("gpm-spectro-mirror", html)
        self.assertIn("gpm-source-text", html)
        self.assertIn("GeometricViewport.renderInto", app_js)
        self.assertIn("replace(/\\r\\n/g", js)
        self.assertIn("syncEditorNormalizedText", app_js)
        self.assertIn("clearGpmEditorSpectroOverlay", app_js)
        self.assertNotIn("scheduleSpectroFromSelection", app_js)
        self.assertIn("initIcurveGeometricLab", app_js)
        self.assertIn("runIcurveSpectroscope", app_js)
        self.assertIn("lockIcurveIngest", app_js)
        self.assertIn("ikurveGpmCache", app_js)
        self.assertIn(".geometric-matrix", css)
        self.assertIn("user-select: text", css)
        self.assertIn(".ikurve-ingest-locked", css)
        self.assertIn("--spectro-teal-rgb", css)


class TestSerializeViewport(unittest.TestCase):
    def test_serialize_viewport_roundtrip_fields(self):
        from ge_prime.hierarchy import serialize_viewport
        from gpm.compiler import compile_text

        text = "Peter sieht Peter.\nZweite Zeile."
        doc, _, _ = compile_text(text)
        payload = serialize_viewport(doc)
        self.assertIn("reconstructed_text", payload)
        self.assertIn("Peter", payload["reconstructed_text"])
        self.assertTrue(payload["structural_lines"])
        self.assertTrue(payload["token_char_map"])
        self.assertTrue(payload["plain_gpm_base64"])
        self.assertEqual(payload["token_char_map"][0]["token_index"], 0)


if __name__ == "__main__":
    unittest.main()
