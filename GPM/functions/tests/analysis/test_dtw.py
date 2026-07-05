"""Tests für DTW auf Substanz-Ketten."""

import unittest

from alphabets import AlphabetProfile
from analysis.geom.dtw import dtw_similarity
from analysis.substance.compare import substance_ggt_kgv_distance
from gpm_types.si import encode_si


class TestDtw(unittest.TestCase):
    def setUp(self):
        self.profile = AlphabetProfile.OG

    def test_identical_sequence_similarity(self):
        words = ["HALLO", "WELT", "TEST"]
        seq = [encode_si(w, self.profile)[0] for w in words]
        result = dtw_similarity(seq, seq, substance_ggt_kgv_distance)
        self.assertFalse(result.failed)
        self.assertAlmostEqual(result.similarity, 1.0, places=4)

    def test_anagram_words_same_substance(self):
        s1, _ = encode_si("LISTEN", self.profile)
        s2, _ = encode_si("SILENT", self.profile)
        result = dtw_similarity([s1], [s2], substance_ggt_kgv_distance)
        self.assertAlmostEqual(result.similarity, 1.0, places=4)

    def test_empty_sequence_fails(self):
        result = dtw_similarity([], [1], substance_ggt_kgv_distance)
        self.assertTrue(result.failed)


if __name__ == "__main__":
    unittest.main()
