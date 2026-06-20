import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ge_prime.compare import (
    compare_substances,
    substance_covers,
    substance_log_distance,
    substance_log_similarity,
    substance_lcm,
    union_letters,
)
from ge_prime.encode import encode_word


class TestSubstanceLcm(unittest.TestCase):
    def test_lcm_mut_wut_union(self):
        s_mut, _ = encode_word("MUT")
        s_wut, _ = encode_word("WUT")
        lcm = substance_lcm(s_mut, s_wut)
        union = union_letters(s_mut, s_wut)
        self.assertEqual(set(union.keys()), {"M", "U", "T", "W"})
        self.assertTrue(substance_covers(lcm, lcm))
        self.assertFalse(substance_covers(s_mut, lcm))
        self.assertFalse(substance_covers(s_wut, lcm))

    def test_mutwut_covers_lcm(self):
        s_mut, _ = encode_word("MUT")
        s_wut, _ = encode_word("WUT")
        s_mutwut, _ = encode_word("MUTWUT")
        lcm = substance_lcm(s_mut, s_wut)
        self.assertTrue(substance_covers(s_mutwut, lcm))

    def test_compare_substances_includes_ggt_kgv(self):
        s1, _ = encode_word("MUT")
        s2, _ = encode_word("WUT")
        cmp = compare_substances(s1, s2)
        self.assertIn("ggt_kgv_similarity", cmp)
        self.assertIn("legacy_similarity_ratio", cmp)
        self.assertIn("kgv_value", cmp)
        self.assertGreater(cmp["ggt_kgv_similarity"], 0.0)
        self.assertLess(cmp["ggt_kgv_similarity"], 1.0)

    def test_substance_ggt_kgv_api_aliases(self):
        s1, _ = encode_word("LISTEN")
        s2, _ = encode_word("SILENT")
        from ge_prime.compare import substance_ggt_kgv_similarity

        self.assertAlmostEqual(substance_ggt_kgv_similarity(s1, s2), substance_log_similarity(s1, s2), places=6)

    def test_compare_substances_includes_lcm(self):
        s1, _ = encode_word("MUT")
        s2, _ = encode_word("WUT")
        cmp = compare_substances(s1, s2)
        self.assertIn("lcm_value", cmp)
        self.assertIn("union_letters", cmp)
        self.assertEqual(cmp["lcm_value"], substance_lcm(s1, s2))
        self.assertEqual(set(cmp["union_letters"].keys()), {"M", "U", "T", "W"})
        self.assertEqual(set(cmp["shared_letters"].keys()), {"U", "T"})

    def test_substance_lcm_rejects_invalid(self):
        with self.assertRaises(ValueError):
            substance_lcm(0, 1)

    def test_substance_log_similarity_anagram_is_one(self):
        s1, _ = encode_word("LISTEN")
        s2, _ = encode_word("SILENT")
        self.assertAlmostEqual(substance_log_similarity(s1, s2), 1.0, places=6)
        self.assertAlmostEqual(substance_log_distance(s1, s2), 0.0, places=6)

    def test_substance_log_similarity_partial_overlap(self):
        s_short, _ = encode_word("MUT")
        s_long, _ = encode_word("MUTWUT")
        sim = substance_log_similarity(s_short, s_long)
        max_sim = substance_log_similarity(s_short, s_short)
        self.assertGreater(sim, 0.0)
        self.assertLess(sim, max_sim)


if __name__ == "__main__":
    unittest.main()
