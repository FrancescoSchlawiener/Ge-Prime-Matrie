import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ge_prime.core import PRIME_MAP
from ge_prime.meta_genome import (
    MIXED_LANGUAGE_RATIO_THRESHOLD,
    assess_structure_matrix,
    build_meta_genome_from_text,
    compare_meta_genomes,
    compare_profiles,
    db_token_language_audit,
    enrich_pair_analysis,
)
from ge_prime.linguistics.profiles import build_prime_profile
from ge_prime.i_curve import analyze_pair
from gpm.compiler import compile_text


class _MockAuditRepo:
    def lookup_languages_bulk(self, normalized_words):
        mapping = {
            "TARGET": {"en": 3},
            "ALGORITHM": {"en": 2},
            "DER": {"de": 5},
            "PATIENT": {"de": 4},
            "ERHÄLT": {"de": 2},
            "EINE": {"de": 10},
            "DIAGNOSE": {"de": 3},
            "UND": {"de": 20, "en": 1},
            "THERAPIE": {"de": 2},
            "IN": {"de": 8, "en": 5},
            "Klinik": {"de": 1},
            "KLINIK": {"de": 1},
        }
        return {w: dict(mapping[w]) for w in normalized_words if w in mapping}

    def count_words_by_language(self, *, exclude_random=True):
        return {"de": 255000, "en": 473000}


class TestDbLanguageAudit(unittest.TestCase):
    def test_audit_off_unavailable(self):
        doc, _, _ = compile_text("Target Algorithm")
        audit = db_token_language_audit(doc, _MockAuditRepo(), "de", db_audit_mode="off")
        self.assertFalse(audit["available"])
        self.assertEqual(audit["reason"], "audit_off")
        self.assertEqual(audit["foreign_tokens"], [])

    def test_build_meta_genome_db_audit_when_language_unknown(self):
        from unittest.mock import patch

        from ge_prime.meta_genome import build_meta_genome

        doc, _, _ = compile_text("der die das und ist in der")
        unknown_lang = {
            "code": "unknown",
            "label": "Unklar",
            "scores": {"de": 0.35, "en": 0.12},
            "confidence": 0.35,
            "method": "hybrid",
            "has_eszett": False,
            "eszett_mass": 0,
        }
        with patch("ge_prime.meta_genome.classify_language", return_value=unknown_lang):
            meta = build_meta_genome(doc, _MockAuditRepo(), db_audit_mode="de_en")
        coverage = meta["language"]["db_coverage"]
        self.assertTrue(coverage["available"])
        self.assertTrue(coverage.get("language_uncertain"))
        self.assertEqual(coverage.get("inferred_lang"), "de")
        self.assertGreater(coverage["unique_tokens"], 0)

    def test_all_db_foreign_tokens(self):
        doc, _, _ = compile_text("Target Algorithm")
        audit = db_token_language_audit(doc, _MockAuditRepo(), "de", db_audit_mode="all_db")
        self.assertTrue(audit["available"])
        self.assertGreaterEqual(len(audit["foreign_tokens"]), 1)
        self.assertEqual(audit["foreign_tokens"][0]["detected_lang"], "en")
        self.assertIn("pool_size", audit["foreign_tokens"][0])

    def test_mixed_language_suspect_at_30_percent(self):
        class BelowRepo(_MockAuditRepo):
            def lookup_languages_bulk(self, normalized_words):
                out = {}
                for i, w in enumerate(normalized_words):
                    if i < 2:
                        out[w] = {"en": 2}
                    else:
                        out[w] = {"de": 2}
                return out

        class AboveRepo(_MockAuditRepo):
            def lookup_languages_bulk(self, normalized_words):
                out = {}
                for i, w in enumerate(normalized_words):
                    if i < 4:
                        out[w] = {"en": 2}
                    else:
                        out[w] = {"de": 2}
                return out

        doc_low, _, _ = compile_text("Alpha Beta Gamma Delta Epsilon Zeta Eta Theta Iota Kappa")
        audit_low = db_token_language_audit(doc_low, BelowRepo(), "de", db_audit_mode="all_db")
        ratio_low = audit_low["other_lang_count"] / audit_low["unique_tokens"]
        self.assertLess(ratio_low, MIXED_LANGUAGE_RATIO_THRESHOLD)

        doc_high, _, _ = compile_text("Alpha Beta Gamma Delta Mu Nu Xi Pi Rho Sigma Tau")
        audit_high = db_token_language_audit(doc_high, AboveRepo(), "de", db_audit_mode="all_db")
        ratio_high = audit_high["other_lang_count"] / audit_high["unique_tokens"]
        self.assertGreaterEqual(ratio_high, MIXED_LANGUAGE_RATIO_THRESHOLD)

        struct = assess_structure_matrix(
            icurve_comparison={"geometry_score": 0.0, "literal_match_ratio": 0.0, "aligned": True},
            meta_a={"language": {"code": "de", "label": "Deutsch", "db_coverage": audit_high}},
            meta_b={"language": {"code": "de", "label": "Deutsch", "db_coverage": audit_high}},
            meta_comparison={"similarity_ratio": 0.0},
            relation_comparison={"relation_score": 0.0},
        )
        self.assertTrue(struct["mixed_language_suspect"])


class TestMetaGenome(unittest.TestCase):
    DE_TEXT = "Der Patient erhält eine Diagnose und Therapie in der Klinik."
    EN_TEXT = "And the man has become very happy today indeed with the government."
    DE_LEGAL = "Der Mandant klagt vor Gericht wegen Vertrag und Paragraph."
    DE_MED = "Patient Diagnose Therapie Symptom Operation Klinik Arzt Behandlung"

    def test_profile_builds_from_document(self):
        doc, _, stats = compile_text(self.DE_TEXT)
        profile = build_prime_profile(doc)
        self.assertGreater(sum(profile.values()), 0)
        self.assertIn(PRIME_MAP["E"], profile)

    def test_meta_genome_has_vector_and_top_words(self):
        doc, _, stats = compile_text(self.DE_TEXT)
        meta = build_meta_genome_from_text(self.DE_TEXT)
        self.assertIn("vector", meta)
        self.assertGreater(meta["vector_bits"], 0)
        self.assertGreater(len(meta["top_words"]), 0)
        self.assertEqual(meta["token_count"], stats.total_tokens)

    def test_german_detects_eszett(self):
        meta = build_meta_genome_from_text("Straße und Fuß sind schön.")
        self.assertTrue(meta["language"]["has_eszett"])
        self.assertEqual(meta["language"]["code"], "de")

    def test_language_german_vs_english(self):
        de = build_meta_genome_from_text(self.DE_TEXT)["language"]
        en = build_meta_genome_from_text(self.EN_TEXT)["language"]
        self.assertEqual(de["code"], "de")
        self.assertEqual(en["code"], "en")

    def test_same_domain_medical_higher_than_cross(self):
        meta_a = build_meta_genome_from_text(self.DE_MED)
        meta_b = build_meta_genome_from_text("Patient mit Symptom und Diagnose in Klinik")
        meta_c = build_meta_genome_from_text(self.DE_LEGAL)
        self.assertEqual(meta_a["domain"]["code"], "medical")
        self.assertEqual(meta_c["domain"]["code"], "legal")
        med_cmp = compare_meta_genomes(meta_a, meta_b)
        cross_cmp = compare_meta_genomes(meta_a, meta_c)
        med_sim = med_cmp["similarity_ratio"]
        cross_sim = cross_cmp["similarity_ratio"]
        self.assertGreater(med_sim, cross_sim)
        self.assertFalse(med_cmp["same_domain"])
        self.assertFalse(cross_cmp["same_domain"])

    def test_same_domain_true_when_profiles_align(self):
        meta_a = build_meta_genome_from_text(self.DE_MED)
        meta_b = build_meta_genome_from_text(self.DE_MED)
        cmp = compare_meta_genomes(meta_a, meta_b)
        self.assertGreaterEqual(cmp["similarity_ratio"], 0.99)
        self.assertTrue(cmp["same_domain"])

    def test_same_domain_requires_profile_overlap(self):
        meta_a = build_meta_genome_from_text(self.DE_MED)
        meta_b = build_meta_genome_from_text(
            "Software Server Algorithmus Datenbank Netzwerk Programm Computer Cloud"
        )
        self.assertEqual(meta_a["domain"]["code"], "medical")
        self.assertEqual(meta_b["domain"]["code"], "tech")
        cmp = compare_meta_genomes(meta_a, meta_b)
        self.assertLess(cmp["similarity_ratio"], 0.12)
        self.assertFalse(cmp["same_domain"])

    def test_analyze_pair_includes_meta(self):
        result = analyze_pair(text_a=self.DE_TEXT, text_b=self.DE_MED)
        self.assertIn("meta_a", result)
        self.assertIn("meta_comparison", result)
        self.assertIn("structure_assessment", result)
        self.assertIn("isomorphism_index", result["structure_assessment"])
        self.assertIn("classification", result["structure_assessment"])

    def test_compare_meta_genomes_large_profile_without_int_limit(self):
        chunk = "Patient Diagnose Therapie Symptom Operation Klinik Arzt Behandlung "
        text_big = chunk * 150
        meta_a = build_meta_genome_from_text(text_big)
        meta_b = build_meta_genome_from_text(text_big)
        self.assertTrue(meta_a["vector"].startswith("∏"))
        cmp = compare_meta_genomes(meta_a, meta_b)
        self.assertGreaterEqual(cmp["similarity_ratio"], 0.99)
        text_icurve = chunk * 80
        result = analyze_pair(text_a=text_icurve, text_b=text_icurve)
        self.assertIn("meta_comparison", result)

    def test_enrich_pair_analysis_structure_fields(self):
        doc_a, _, _ = compile_text(self.DE_TEXT)
        doc_b, _, _ = compile_text(self.DE_MED)
        from ge_prime.i_curve import compare_i_curves, extract_i_curve, extract_substance_curve

        cmp = compare_i_curves(
            extract_i_curve(doc_a),
            extract_i_curve(doc_b),
            substance_a=extract_substance_curve(doc_a),
            substance_b=extract_substance_curve(doc_b),
        )
        enriched = enrich_pair_analysis(doc_a, doc_b, cmp)
        self.assertIn("interpretation", enriched["structure_assessment"])
        self.assertIn("signals", enriched["structure_assessment"])
        self.assertNotIn("highlight", enriched["structure_assessment"])
        self.assertIn("relation_comparison", enriched)
        self.assertIn("relation_score", enriched["meta_comparison"])

    def test_compare_profiles_exposes_ggt_diagnostics(self):
        doc_a, _, _ = compile_text(self.DE_MED)
        doc_b, _, _ = compile_text(self.DE_MED)
        profile_a = build_prime_profile(doc_a)
        profile_b = build_prime_profile(doc_b)
        cmp = compare_profiles(profile_a, profile_b)
        self.assertIn("log_gcd", cmp)
        self.assertIn("log_a", cmp)
        self.assertIn("log_b", cmp)
        self.assertIn("shared_prime_entries", cmp)
        self.assertGreater(cmp["shared_prime_count"], 0)
        self.assertIsNone(cmp["zero_reason"])
        self.assertGreaterEqual(cmp["similarity_ratio"], 0.99)

    def test_compare_meta_genomes_includes_meta_ggt_diagnostics(self):
        meta_a = build_meta_genome_from_text(self.DE_MED)
        meta_b = build_meta_genome_from_text("Patient mit Symptom und Diagnose in Klinik")
        cmp = compare_meta_genomes(meta_a, meta_b)
        diag = cmp["meta_ggt_diagnostics"]
        self.assertIn("log_gcd", diag)
        self.assertIn("shared_prime_entries", diag)
        self.assertGreater(diag["shared_prime_count"], 0)


if __name__ == "__main__":
    unittest.main()
