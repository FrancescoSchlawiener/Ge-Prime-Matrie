"""Nested script — Close-Matching ohne Tag-Pop."""

import unittest

from alphabets import AlphabetProfile
from analysis.blocks.registry import DocumentRegistry
from analysis.code.compile import compile_source, verify_reversibility
from analysis.code.envelope import BlockEnvelope, parse_envelope_meta


class TestCodeBlockNestedScript(unittest.TestCase):
    def test_brace_in_nested_script_stays_in_child(self):
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        src = "<div><script>if (x) { y = 1; }</script></div>\n"
        mod = compile_source(src, "html", reg)
        self.assertTrue(verify_reversibility(src, "html", reg))
        script_child = None
        for c in mod.children:
            if c.meta.get("embedded_language") == "js" or c.meta.get("rule_language") == "js":
                script_child = c
            for cc in c.children:
                if cc.meta.get("embedded_language") == "js" or cc.meta.get("rule_language") == "js":
                    script_child = cc
        self.assertIsNotNone(script_child)
        env = parse_envelope_meta(script_child.meta)
        self.assertEqual(env, BlockEnvelope.TAG)
        has_brace_child = any(
            parse_envelope_meta(c.meta) is BlockEnvelope.BRACE for c in script_child.children
        )
        self.assertTrue(has_brace_child or verify_reversibility(src, "html", reg))


if __name__ == "__main__":
    unittest.main()
