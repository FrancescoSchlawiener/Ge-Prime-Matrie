import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ge_prime.payload_codec import compress_rhythm_breaks, compress_spectro_matches


class TestPayloadCodec(unittest.TestCase):
    def test_merge_only_contiguous_tokens(self):
        matches = [
            {"mode": "anagram_shadow", "layer": "semantic", "token_start": 0, "token_end": 2},
            {"mode": "anagram_shadow", "layer": "semantic", "token_start": 2, "token_end": 4},
            {"mode": "anagram_shadow", "layer": "semantic", "token_start": 5, "token_end": 6},
        ]
        out = compress_spectro_matches(matches)
        same_mode = [m for m in out if m["mode"] == "anagram_shadow"]
        self.assertEqual(len(same_mode), 2)
        self.assertEqual(same_mode[0]["token_start"], 0)
        self.assertEqual(same_mode[0]["token_count"], 4)
        self.assertEqual(same_mode[1]["token_start"], 5)
        self.assertEqual(same_mode[1]["token_count"], 1)

    def test_no_merge_across_token_gap(self):
        matches = [
            {"mode": "substance_divisor", "layer": "semantic", "token_start": 0, "token_end": 1},
            {"mode": "substance_divisor", "layer": "semantic", "token_start": 2, "token_end": 3},
        ]
        out = compress_spectro_matches(matches)
        self.assertEqual(len(out), 2)

    def test_compress_rhythm_breaks_strips_inter_fields(self):
        breaks = [
            {
                "sentence_start": 0,
                "sentence_count": 3,
                "line_start": 1,
                "line_count": 2,
                "inter_start": 1,
                "inter_end": 2,
            }
        ]
        out = compress_rhythm_breaks(breaks)
        self.assertEqual(out[0]["sentence_start"], 0)
        self.assertNotIn("inter_start", out[0])


if __name__ == "__main__":
    unittest.main()
