import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ge_prime.language_detect import (
    KANONISCHER_MATRIX_RICHTWERT,
    MIN_SIGNAL_WEIGHT_BUDGET,
    PREVIEW_TOKEN_LIMIT,
    build_meta_genome_db_audit,
    merge_db_speech_audit,
)
from ge_prime.linguistics.registry import LANGUAGE_MIN_CONFIDENCE
from gpm.compiler import compile_text


class _VectorRepo:
    def __init__(self, mapping):
        self._mapping = mapping

    def lookup_languages_bulk(self, normalized_words):
        return {w: dict(self._mapping[w]) for w in normalized_words if w in self._mapping}

    def count_words_by_language(self, *, exclude_random=True):
        return {"de": 1000, "en": 1000}


class TestLanguageDetect(unittest.TestCase):
    def test_preview_uses_word_normalized_only(self):
        doc, _, _ = compile_text("der die das")
        repo = _VectorRepo({"DER": {"de": 2}, "DIE": {"de": 2}, "DAS": {"de": 2}})
        audit = build_meta_genome_db_audit(doc, {"code": "de"}, repo, db_audit_mode="de_en")
        self.assertEqual(audit["audit_status"], "VERIFIED")
        self.assertGreater(audit["confidence"], KANONISCHER_MATRIX_RICHTWERT)
        self.assertIn("de", audit["vector_distribution"])

    def test_empty_vector_is_critical(self):
        doc, _, _ = compile_text("xyzzy qwerty")
        repo = _VectorRepo({})
        audit = build_meta_genome_db_audit(doc, {"code": "unknown"}, repo, db_audit_mode="de_en")
        self.assertEqual(audit["audit_status"], "CRITICAL_ANOMALY")
        self.assertTrue(audit["language_uncertain"])
        self.assertEqual(audit["confidence"], 0.0)
        self.assertEqual(audit["primary_language"], "unknown")

    def test_verified_when_confidence_high(self):
        doc, _, _ = compile_text("der der der der der")
        repo = _VectorRepo({"DER": {"de": 10, "en": 1}})
        audit = build_meta_genome_db_audit(doc, {"code": "de"}, repo, db_audit_mode="de_en")
        self.assertEqual(audit["audit_status"], "VERIFIED")
        self.assertFalse(audit["language_uncertain"])
        self.assertGreaterEqual(audit["confidence"], KANONISCHER_MATRIX_RICHTWERT)

    def test_classified_de_not_overridden_by_weak_vector(self):
        doc, _, _ = compile_text("alpha beta gamma")
        repo = _VectorRepo(
            {
                "ALPHA": {"de": 3.5, "en": 6.5},
                "BETA": {"de": 3.5, "en": 6.5},
                "GAMMA": {"de": 3.5, "en": 6.5},
            }
        )
        language = {
            "code": "de",
            "label": "Deutsch",
            "confidence": LANGUAGE_MIN_CONFIDENCE + 0.02,
            "method": "hybrid",
        }
        audit = build_meta_genome_db_audit(doc, language, repo, db_audit_mode="de_en")
        self.assertFalse(audit["language_uncertain"])
        self.assertEqual(audit["audit_status"], "VERIFIED")
        self.assertEqual(audit["expected_lang"], "de")

    def test_uncertain_when_weak_vector_tendency(self):
        doc, _, _ = compile_text("alpha beta gamma")
        repo = _VectorRepo(
            {
                "ALPHA": {"de": 3.5, "en": 3.3, "fr": 3.2},
                "BETA": {"de": 3.5, "en": 3.3, "fr": 3.2},
                "GAMMA": {"de": 3.5, "en": 3.3, "fr": 3.2},
            }
        )
        audit = build_meta_genome_db_audit(doc, {"code": "unknown"}, repo, db_audit_mode="de_en")
        self.assertLess(audit["confidence"], KANONISCHER_MATRIX_RICHTWERT)
        self.assertGreaterEqual(audit["vector_distribution"]["de"], MIN_SIGNAL_WEIGHT_BUDGET)
        self.assertTrue(audit["language_uncertain"])
        self.assertEqual(audit["audit_status"], "UNCERTAIN")

    def test_noise_below_threshold_is_critical(self):
        doc, _, _ = compile_text("one")
        repo = _VectorRepo({"ONE": {"de": 0.35, "en": 0.33, "fr": 0.32}})
        audit = build_meta_genome_db_audit(doc, {"code": "unknown"}, repo, db_audit_mode="de_en")
        self.assertEqual(audit["audit_status"], "CRITICAL_ANOMALY")

    def test_merge_db_speech_audit_picks_worst(self):
        verified = {"audit_status": "VERIFIED", "language_uncertain": False}
        critical = {"audit_status": "CRITICAL_ANOMALY", "language_uncertain": True}
        uncertain = {"audit_status": "UNCERTAIN", "language_uncertain": True}
        self.assertEqual(merge_db_speech_audit(verified, critical)["audit_status"], "CRITICAL_ANOMALY")
        self.assertEqual(merge_db_speech_audit(verified, uncertain)["audit_status"], "UNCERTAIN")

    def test_preview_token_limit_constant(self):
        self.assertEqual(PREVIEW_TOKEN_LIMIT, 30)
