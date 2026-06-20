import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from db.repository import WordRepository
from ge_prime.linguistics import (
    LanguageSpec,
    classify_domain,
    classify_language,
    register_language,
    resolve_db_audit_language,
)
from ge_prime.linguistics.profiles import build_prime_profile, clear_profile_caches
from ge_prime.linguistics.registry import MIN_DB_WORDS_PER_LANGUAGE
from ge_prime.meta_genome import build_meta_genome_from_text
from ge_prime.i_curve import analyze_pair
from gpm.compiler import compile_text
from pipeline.process import process_word


class TestLinguisticsLanguage(unittest.TestCase):
    DE_TEXT = "Der Patient erhält eine Diagnose und Therapie in der Klinik."
    EN_TEXT = "And the man has become very happy today indeed with the government."
    SHORT = "Hallo Welt"

    def _classify(self, text, repo=None):
        doc, _, _ = compile_text(text)
        profile = build_prime_profile(doc)
        return classify_language(doc, profile, repo)

    def test_german_medical_text(self):
        result = self._classify(self.DE_TEXT)
        self.assertEqual(result["code"], "de")
        self.assertGreater(result["confidence"], 0.45)

    def test_english_text(self):
        result = self._classify(self.EN_TEXT)
        self.assertEqual(result["code"], "en")

    def test_short_text_unclear_or_low_confidence(self):
        result = self._classify(self.SHORT)
        self.assertIn(result["code"], ("de", "en", "unknown"))

    def test_empty_repo_skips_db_tier(self):
        with tempfile.TemporaryDirectory() as tmp:
            clear_profile_caches()
            repo = WordRepository(Path(tmp) / "empty.db")
            repo.init_db()
            self.assertEqual(repo.total_count(), 0)
            result = self._classify(self.DE_TEXT, repo=repo)
            self.assertEqual(result["code"], "de")
            self.assertEqual(result["method"], "patterns")

    def test_unknown_language_scores_resolve_de_for_db_audit(self):
        lang = {
            "code": "unknown",
            "label": "Unklar",
            "scores": {"de": 0.35, "en": 0.12},
            "method": "hybrid",
        }
        audit_lang, uncertain = resolve_db_audit_language(lang)
        self.assertEqual(audit_lang, "de")
        self.assertTrue(uncertain)

    def test_db_tier_when_enough_words(self):
        with tempfile.TemporaryDirectory() as tmp:
            clear_profile_caches()
            repo = WordRepository(Path(tmp) / "ling.db")
            repo.init_db()
            source_id = repo.get_or_create_source("test", "test")
            words = []
            for token in (
                "der die das und ist ein eine nicht auf mit fuer auch nach bei wird sind "
                "haben oder aber wenn ueber durch kann sein werden patient diagnose therapie"
            ).split():
                w = process_word(token, language="de", source="test")
                if w:
                    words.append(w)
            pad = 0
            while len(words) < MIN_DB_WORDS_PER_LANGUAGE:
                pad += 1
                # process_word lehnt Ziffern ab — nur Buchstaben als Füllwörter
                w = process_word(f"lexem{chr(ord('a') + pad - 1)}", language="de", source="test")
                if w:
                    words.append(w)
                elif pad > 64:
                    self.fail("Konnte nicht genug DE-Wörter für DB-Tier-Test erzeugen")
            repo.insert_words_batch(words, source_id)
            self.assertGreaterEqual(repo.count_words_by_language()["de"], MIN_DB_WORDS_PER_LANGUAGE)
            result = self._classify(self.DE_TEXT, repo=repo)
            self.assertEqual(result["code"], "de")
            self.assertEqual(result["method"], "hybrid")

    def test_pad_words_with_digits_are_rejected(self):
        """Regression: wort28 enthält Ziffern → None → früher Endlosschleife im DB-Tier-Test."""
        self.assertIsNone(process_word("wort28", language="de", source="test"))
        self.assertIsNotNone(process_word("lexema", language="de", source="test"))


class TestLinguisticsDomain(unittest.TestCase):
    def _classify(self, text, lang="de"):
        doc, _, _ = compile_text(text)
        profile = build_prime_profile(doc)
        return classify_domain(doc, profile, lang)

    def test_medical_german(self):
        text = "Patient Diagnose Therapie Symptom Operation Klinik Arzt Behandlung Krankheit"
        result = self._classify(text)
        self.assertEqual(result["code"], "medical")
        self.assertFalse(result["fallback"])

    def test_legal_german(self):
        text = "Der Mandant klagt vor Gericht wegen Vertrag und Paragraph Urteil Anwalt Gesetz"
        result = self._classify(text)
        self.assertEqual(result["code"], "legal")

    def test_legal_english(self):
        text = "The plaintiff filed a lawsuit in court regarding the contract clause and statute evidence"
        result = self._classify(text, lang="en")
        self.assertEqual(result["code"], "legal")

    def test_tech_domain(self):
        text = "Software Server Algorithmus Datenbank Netzwerk Programm Computer Cloud Entwickler Code"
        result = self._classify(text)
        self.assertEqual(result["code"], "tech")

    def test_business_domain(self):
        text = "Unternehmen Umsatz Markt Investition Kunde Gewinn Finanz Bank Verkauf Strategie"
        result = self._classify(text)
        self.assertEqual(result["code"], "business")

    def test_science_domain(self):
        text = "Forschung Studie Hypothese Experiment Methode Ergebnis Daten Analyse Theorie Labor"
        result = self._classify(text)
        self.assertEqual(result["code"], "science")

    def test_education_domain(self):
        text = "Schule Universitaet Student Lehrer lernen Unterricht Pruefung Kurs Seminar Professor"
        result = self._classify(text)
        self.assertEqual(result["code"], "education")

    def test_news_domain(self):
        text = "Es berichtet die Regierung der Minister zur Wahl Ereignis Nachrichten Presse Journalist Parlament"
        result = self._classify(text)
        self.assertEqual(result["code"], "news")

    def test_casual_text_falls_back_to_general(self):
        text = "Heute gehe ich spazieren und esse Brot mit Butter am See."
        result = self._classify(text)
        self.assertEqual(result["code"], "general")
        self.assertTrue(result["fallback"])

    def test_matched_keywords_present_for_medical(self):
        text = "Patient mit Diagnose und Therapie in der Klinik"
        result = self._classify(text)
        self.assertGreaterEqual(len(result.get("matched_keywords", [])), 1)


class TestLinguisticsExtensibility(unittest.TestCase):
    def test_register_language_stub(self):
        spec = LanguageSpec(
            code="fr",
            label="Französisch",
            function_words=frozenset({"LE", "LA", "ET", "EST", "UN", "UNE"}),
            profile_seed="le la et est un une de des du",
        )
        register_language(spec)
        doc, _, _ = compile_text("le la et est un une de des du maison")
        profile = build_prime_profile(doc)
        result = classify_language(doc, profile)
        self.assertIn("fr", result["scores"])


class TestMetaGenomeIntegration(unittest.TestCase):
    DE_MED = "Der Patient erhält Diagnose und Therapie in der Klinik."

    def test_build_meta_includes_method_and_domain_fields(self):
        meta = build_meta_genome_from_text("Der Patient erhält Diagnose und Therapie.")
        self.assertIn("method", meta["language"])
        self.assertIn("fallback", meta["domain"])
        self.assertEqual(meta["domain"]["code"], "medical")

    def test_analyze_pair_wires_language_and_domain(self):
        result = analyze_pair(text_a=self.DE_MED, text_b=self.DE_MED)
        for key in ("meta_a", "meta_b", "meta_comparison", "plagiarism_assessment"):
            self.assertIn(key, result)
        self.assertEqual(result["meta_a"]["language"]["code"], "de")
        self.assertEqual(result["meta_a"]["domain"]["code"], "medical")
        self.assertFalse(result["meta_a"]["domain"]["fallback"])
        self.assertIn("same_domain", result["meta_comparison"])
        self.assertIn("interpretation", result["plagiarism_assessment"])

    def test_analyze_pair_db_tier_hybrid(self):
        from db.repository import WordRepository
        from ge_prime.linguistics.profiles import clear_profile_caches, db_tier_available

        repo = WordRepository()
        repo.init_db()
        if not db_tier_available(repo):
            self.skipTest("DB-Tier nicht aktiv — scrape.py --source all ausführen")

        clear_profile_caches()
        result = analyze_pair(text_a=self.DE_MED, text_b=self.DE_MED, repo=repo)
        self.assertEqual(result["meta_a"]["language"]["method"], "hybrid")
        self.assertEqual(result["meta_a"]["language"]["code"], "de")


if __name__ == "__main__":
    unittest.main()
