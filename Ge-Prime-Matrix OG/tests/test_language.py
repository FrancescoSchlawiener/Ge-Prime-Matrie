import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from db.language import LANGUAGE_RANDOM, language_label, resolve_language
from ge_prime.linguistics.language import infer_text_language_code
from pipeline.process import process_token, process_word


class TestLanguage(unittest.TestCase):
    def test_explicit_language(self):
        self.assertEqual(resolve_language("de"), "de")
        self.assertEqual(resolve_language(" EN "), "en")

    def test_missing_language_is_random(self):
        self.assertEqual(resolve_language(None), LANGUAGE_RANDOM)
        self.assertEqual(resolve_language(""), LANGUAGE_RANDOM)

    def test_language_label(self):
        self.assertEqual(language_label("random"), "Random / unsortiert")
        self.assertEqual(language_label("de"), "Deutsch")

    def test_process_word_random_by_default(self):
        r = process_word("HALLO", source="test")
        self.assertIsNotNone(r)
        self.assertEqual(r.language, LANGUAGE_RANDOM)

    def test_process_token_random_by_default(self):
        r = process_token("HALLO!", source="web")
        self.assertIsNotNone(r)
        self.assertEqual(r.language, LANGUAGE_RANDOM)

    def test_infer_text_language_german(self):
        self.assertEqual(infer_text_language_code("Der Patient erhält Therapie."), "de")

    def test_infer_text_language_english(self):
        self.assertEqual(
            infer_text_language_code(
                "And the man has become very happy today indeed with the government."
            ),
            "en",
        )

    def test_infer_short_ambiguous_is_random(self):
        self.assertEqual(infer_text_language_code("HALLO"), LANGUAGE_RANDOM)


if __name__ == "__main__":
    unittest.main()
