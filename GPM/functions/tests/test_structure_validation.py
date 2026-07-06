"""Tests für Struktur-Validierungspipeline."""

import unittest

from alphabets import AlphabetProfile
from analysis.blocks.build import materialize_geometry
from analysis.compile.compiler import compile_text
from analysis.meta.enrich import enrich_pair_analysis
from analysis.validation.structure import (
    STEP_IDS,
    build_validation_pipeline,
    classify_structure_pattern,
    compare_enjambement_phases,
    pair_relevance_prefilter,
)


class TestStructureValidation(unittest.TestCase):
    TEXT_A = "Zeile eins.\nZeile zwei."
    TEXT_B = "Andere Zeile.\nNoch eine."

    def test_step_ids_include_meta_profile_audit(self):
        self.assertIn("meta_profile_audit", STEP_IDS)
        self.assertNotIn("db_matrix_audit", STEP_IDS)

    def test_pair_relevance_prefilter(self):
        doc_a, _ = compile_text(self.TEXT_A, AlphabetProfile.OG)
        doc_b, _ = compile_text(self.TEXT_B, AlphabetProfile.OG)
        materialize_geometry(doc_a)
        materialize_geometry(doc_b)
        pre = pair_relevance_prefilter(doc_a, doc_b)
        self.assertTrue(pre["relevant"])
        self.assertTrue(pre["interval_index_a"])

    def test_classify_literal_identity(self):
        result = classify_structure_pattern(
            word_geo=1.0,
            substance_score=0.5,
            literal=1.0,
            combined=0.9,
            relation_score=0.5,
            enjambement_phase={},
            structural_waveform_parallel=True,
        )
        self.assertEqual(result, "literal_identity")

    def test_classify_independent(self):
        result = classify_structure_pattern(
            word_geo=0.1,
            substance_score=0.1,
            literal=0.1,
            combined=0.1,
            relation_score=0.1,
            enjambement_phase={},
            structural_waveform_parallel=False,
        )
        self.assertEqual(result, "independent")

    def test_validation_pipeline_step5_meta_audit(self):
        doc_a, _ = compile_text("Hallo Welt.", AlphabetProfile.OG)
        doc_b, _ = compile_text("Hallo Welt.", AlphabetProfile.OG)
        materialize_geometry(doc_a)
        materialize_geometry(doc_b)
        enriched = enrich_pair_analysis(
            doc_a,
            doc_b,
            {"geometry_score": 1.0, "literal_match_ratio": 1.0, "aligned": True},
        )
        pipeline = build_validation_pipeline(
            document_a=doc_a,
            document_b=doc_b,
            comparison={"geometry_score": 1.0, "literal_match_ratio": 1.0},
            hierarchy_comparison={},
            cross_a={},
            cross_b={},
            structure_assessment=enriched["structure_assessment"],
            meta_comparison=enriched["meta_comparison"],
        )
        step5 = pipeline["steps"][4]
        self.assertEqual(step5["id"], "meta_profile_audit")
        self.assertIn(step5["status"], ("ok", "warn", "skip"))

    def test_compare_enjambement_phases(self):
        cross_a = {"rhythm_break_count": 2, "enjambement_profile": "rhythm_break"}
        cross_b = {"rhythm_break_count": 0, "enjambement_profile": "prose_flow"}
        phase = compare_enjambement_phases(cross_a, cross_b)
        self.assertTrue(phase["phase_shift_detected"])


if __name__ == "__main__":
    unittest.main()
