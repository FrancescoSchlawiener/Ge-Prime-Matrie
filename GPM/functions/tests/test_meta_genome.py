"""Tests für Meta-Genom (ohne DB/Linguistics)."""

import unittest

from alphabets import AlphabetProfile
from analysis.compile.compiler import compile_text
from analysis.meta import (
    build_meta_genome,
    build_meta_genome_from_text,
    compare_meta_genomes,
    compare_profiles,
)
from analysis.profile.prime_profile import build_prime_profile


class TestMetaGenome(unittest.TestCase):
    DE_TEXT = "Der Patient erhält eine Diagnose und Therapie in der Klinik."
    DE_MED = "Patient Diagnose Therapie Symptom Operation Klinik Arzt Behandlung"

    def test_meta_genome_has_vector_and_top_words(self):
        doc, stats = compile_text(self.DE_TEXT, AlphabetProfile.OG)
        meta = build_meta_genome_from_text(self.DE_TEXT)
        self.assertIn("vector", meta)
        self.assertGreater(meta["vector_bits"], 0)
        self.assertGreater(len(meta["top_words"]), 0)
        self.assertEqual(meta["token_count"], stats.word_count)
        self.assertEqual(meta["document_profile"], "og")

    def test_compare_profiles_identical(self):
        doc_a, _ = compile_text(self.DE_MED, AlphabetProfile.OG)
        profile_a = build_prime_profile(doc_a)
        profile_b = build_prime_profile(doc_a)
        cmp = compare_profiles(profile_a, profile_b, document_profile=AlphabetProfile.OG)
        self.assertIn("log_gcd", cmp)
        self.assertGreater(cmp["shared_prime_count"], 0)
        self.assertIsNone(cmp["zero_reason"])
        self.assertGreaterEqual(cmp["similarity_ratio"], 0.99)

    def test_compare_meta_genomes_similar_texts(self):
        meta_a = build_meta_genome_from_text(self.DE_MED)
        meta_b = build_meta_genome_from_text("Patient mit Symptom und Diagnose in Klinik")
        cmp = compare_meta_genomes(meta_a, meta_b)
        self.assertGreater(cmp["similarity_ratio"], 0.0)
        self.assertIn("meta_ggt_diagnostics", cmp)

    def test_compare_meta_genomes_identical(self):
        meta_a = build_meta_genome_from_text(self.DE_MED)
        meta_b = build_meta_genome_from_text(self.DE_MED)
        cmp = compare_meta_genomes(meta_a, meta_b)
        self.assertGreaterEqual(cmp["similarity_ratio"], 0.99)

    def test_large_profile_vector_label(self):
        chunk = "Patient Diagnose Therapie Symptom Operation Klinik Arzt Behandlung "
        text_big = chunk * 150
        meta = build_meta_genome_from_text(text_big)
        self.assertTrue(meta["vector"].startswith("∏") or meta["vector"].isdigit())

    def test_enrich_pair_analysis_structure_fields(self):
        from analysis.meta.enrich import enrich_pair_analysis

        doc_a, _ = compile_text(self.DE_TEXT, AlphabetProfile.OG)
        doc_b, _ = compile_text(self.DE_MED, AlphabetProfile.OG)
        cmp = {"geometry_score": 0.3, "literal_match_ratio": 0.2, "aligned": False}
        enriched = enrich_pair_analysis(doc_a, doc_b, cmp)
        self.assertIn("interpretation", enriched["structure_assessment"])
        self.assertIn("signals", enriched["structure_assessment"])
        self.assertIn("relation_comparison", enriched)
        self.assertIn("relation_score", enriched["meta_comparison"])

    def test_build_meta_genome_direct(self):
        doc, _ = compile_text("Hallo Welt", AlphabetProfile.OG)
        meta = build_meta_genome(doc)
        self.assertEqual(meta["unique_words"], len(doc.header))


if __name__ == "__main__":
    unittest.main()
