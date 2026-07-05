import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ge_prime.relation_profile import (
    build_relation_profile,
    compare_relation_profiles,
    relation_twins,
    serialize_relation_comparison_api,
)
from gpm.compiler import compile_text


class TestRelationProfile(unittest.TestCase):
    DE_MED = "Patient Diagnose Therapie Symptom Operation Klinik Arzt Behandlung"
    DE_MED2 = "Patient Diagnose Therapie Symptom Operation Klinik Arzt Behandlung extra"

    def test_build_profile_has_bigrams(self):
        doc, _, _ = compile_text(self.DE_MED)
        prof = build_relation_profile(doc)
        self.assertGreater(prof["bigram_count"], 0)
        self.assertGreater(len(prof["word_bigrams"]), 0)

    def test_similar_texts_higher_relation_score(self):
        doc_a, _, _ = compile_text(self.DE_MED)
        doc_b, _, _ = compile_text(self.DE_MED2)
        doc_c, _, _ = compile_text("Software Server Algorithmus Netzwerk Cloud Programm")
        prof_a = build_relation_profile(doc_a)
        prof_b = build_relation_profile(doc_b)
        prof_c = build_relation_profile(doc_c)
        med_cmp = compare_relation_profiles(prof_a, prof_b)
        cross_cmp = compare_relation_profiles(prof_a, prof_c)
        self.assertGreater(med_cmp["relation_score"], cross_cmp["relation_score"])
        self.assertGreater(len(med_cmp["shared_word_bigrams"]), 0)

    def test_relation_twins_flag(self):
        doc_a, _, _ = compile_text(self.DE_MED)
        doc_b, _, _ = compile_text(self.DE_MED2)
        cmp = compare_relation_profiles(
            build_relation_profile(doc_a),
            build_relation_profile(doc_b),
        )
        self.assertTrue(relation_twins(cmp, literal_match_ratio=0.2))

    def test_identical_profiles_score_one(self):
        doc, _, _ = compile_text(self.DE_MED)
        prof = build_relation_profile(doc)
        cmp = compare_relation_profiles(prof, prof)
        self.assertGreaterEqual(cmp["relation_score"], 0.99)

    def test_serialize_relation_spans(self):
        doc_a, _, _ = compile_text(self.DE_MED)
        doc_b, _, _ = compile_text(self.DE_MED2)
        cmp = compare_relation_profiles(
            build_relation_profile(doc_a),
            build_relation_profile(doc_b),
        )
        api = serialize_relation_comparison_api(cmp, doc_a, doc_b)
        self.assertIn("shared_bigram_spans", api)
        self.assertIn("shared_word_bigrams", api)
        for span in api["shared_bigram_spans"]:
            self.assertGreaterEqual(span["token_start_a"], 0)
            self.assertGreaterEqual(span["token_start_b"], 0)
            self.assertEqual(span["token_count"], 2)


if __name__ == "__main__":
    unittest.main()
