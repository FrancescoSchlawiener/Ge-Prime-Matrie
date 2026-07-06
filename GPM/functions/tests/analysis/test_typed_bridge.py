"""Tests für typed_bridge sketches."""

import unittest

from alphabets import AlphabetProfile
from analysis.algebra.typed_bridge import document_di_sketch, document_ni_sketch
from analysis.compile.compiler import compile_text


class TestTypedBridge(unittest.TestCase):
    def test_ni_sketch_empty_for_plain_text(self):
        doc, _ = compile_text("Hallo", AlphabetProfile.OG)
        self.assertEqual(document_ni_sketch(doc.tokens), tuple())

    def test_di_sketch_from_explicit(self):
        doc, _ = compile_text("Hallo 4,16 Ende.", AlphabetProfile.OG)
        sketch = document_di_sketch(doc)
        self.assertIsInstance(sketch, tuple)


if __name__ == "__main__":
    unittest.main()
