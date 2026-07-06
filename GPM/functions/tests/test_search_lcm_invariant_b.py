import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from alphabets import AlphabetProfile
from analysis.binary.format import read_gpm
from analysis.binary.search import search_by_lcm
from analysis.compile.compiler import compile_text_to_gpm
from analysis.substance.compare import substance_covers, substance_lcm
from gpm_types.si.codec import encode_si


class TestSearchLcmInvariantB(unittest.TestCase):
    def test_mut_wut_og_parity(self):
        _, blob, _ = compile_text_to_gpm("MUTWUT MUT WUT", AlphabetProfile.OG)
        doc = read_gpm(blob)
        result = search_by_lcm(doc, "MUT", "WUT")
        originals = {m["original"] for m in result["matches"]}
        self.assertIn("mutwut", originals)
        self.assertNotIn("mut", originals)
        self.assertNotIn("wut", originals)
        self.assertEqual(set(result["union_letters"].keys()), {"M", "U", "T", "W"})

    def test_three_word_kgv_fold(self):
        _, blob, _ = compile_text_to_gpm("ABCD AB AC AD", AlphabetProfile.OG)
        doc = read_gpm(blob)
        result = search_by_lcm(doc, "AB", "AC", "AD")
        s1, _ = encode_si("AB", AlphabetProfile.OG)
        s2, _ = encode_si("AC", AlphabetProfile.OG)
        s3, _ = encode_si("AD", AlphabetProfile.OG)
        expected_lcm = substance_lcm(substance_lcm(s1, s2), s3)
        self.assertEqual(result["lcm_value"], expected_lcm)

    def test_gcd_only_does_not_match_lcm(self):
        _, blob, _ = compile_text_to_gpm("MUT WUT", AlphabetProfile.OG)
        doc = read_gpm(blob)
        s_mut, _ = encode_si("MUT", AlphabetProfile.OG)
        s_wut, _ = encode_si("WUT", AlphabetProfile.OG)
        search_lcm = substance_lcm(s_mut, s_wut)
        for entry in doc.header:
            if entry.word_canonical.lower() in ("mut", "wut"):
                self.assertFalse(substance_covers(entry.substance, search_lcm))


if __name__ == "__main__":
    unittest.main()
