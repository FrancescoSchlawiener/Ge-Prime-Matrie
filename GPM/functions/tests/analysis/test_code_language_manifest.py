"""Tests für language_manifest — Primary + eingebettete Sprachen."""

from __future__ import annotations

import unittest

from analysis.code.manifest import language_manifest, scan_embedded_languages


class TestLanguageManifest(unittest.TestCase):
    def test_html_with_script_and_style(self):
        src = "<html><style>.a{}</style><script>let x=1;</script></html>"
        m = language_manifest(src, "index.html")
        self.assertEqual(m["primary"], "html")
        self.assertEqual(m["embedded"], ["css", "js"])
        self.assertEqual(m["all"], ["css", "html", "js"])

    def test_js_only_no_embedded(self):
        m = language_manifest("function f() {}", "app.js")
        self.assertEqual(m["primary"], "js")
        self.assertEqual(m["embedded"], [])
        self.assertEqual(m["all"], ["js"])

    def test_scan_embedded_empty_for_py(self):
        self.assertEqual(scan_embedded_languages("<script>x</script>", "py"), [])


if __name__ == "__main__":
    unittest.main()
