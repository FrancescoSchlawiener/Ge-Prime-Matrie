"""F-A + E-A — scan_windows profile-Pfad: window_lcm-Metadaten + Log-Score."""

import unittest
from unittest.mock import patch

from alphabets import AlphabetProfile
from analysis.compile.compiler import compile_text
from analysis.index.substance_index import (
    build_substance_index,
    scan_windows,
    window_fingerprint,
)


class TestScanWindowsProfile(unittest.TestCase):
    def test_profile_path_sets_window_lcm_metadata(self):
        doc, _ = compile_text("Hallo Welt Freunde.", AlphabetProfile.OG)
        idx = build_substance_index(doc)
        target = window_fingerprint(idx, 0, 2)
        matches = scan_windows(
            idx,
            2,
            target,
            modes=["anagram_shadow"],
            profile=AlphabetProfile.OG,
        )
        if matches:
            self.assertIn("window_lcm", matches[0])
            self.assertGreater(matches[0]["window_lcm"], 0)

    def test_fingerprint_similarity_called_with_profile(self):
        doc, _ = compile_text("Test Satz.", AlphabetProfile.OG)
        idx = build_substance_index(doc)
        target = window_fingerprint(idx, 0, 1)
        with patch(
            "analysis.index.substance_index.fingerprint_similarity",
            return_value=0.99,
        ) as mock_fp:
            scan_windows(idx, 1, target, modes=["anagram_shadow"], profile=AlphabetProfile.OG)
            self.assertTrue(mock_fp.called)
            for call in mock_fp.call_args_list:
                self.assertEqual(call.kwargs.get("profile"), AlphabetProfile.OG)


if __name__ == "__main__":
    unittest.main()
