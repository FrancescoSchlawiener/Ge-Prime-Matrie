import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pipeline.tokenize import extract_encode_words, letters_only
from web.handlers._steps import build_encode_batch


class TestTokenize(unittest.TestCase):
    def test_letters_only_strips_punctuation_and_digits(self):
        self.assertEqual(letters_only("hello!"), "hello")
        self.assertEqual(letters_only("test123"), "test")
        self.assertEqual(letters_only("Straße."), "Straße")

    def test_extract_words_ignores_spaces_and_junk(self):
        words, skipped, truncated = extract_encode_words("Hallo, Welt! 123 foo")
        self.assertEqual(words, ["Hallo", "Welt", "foo"])
        self.assertEqual(skipped, 1)
        self.assertFalse(truncated)

    def test_extract_max_fifty(self):
        text = " ".join(f"w{i}" for i in range(60))
        words, _, truncated = extract_encode_words(text)
        self.assertEqual(len(words), 50)
        self.assertTrue(truncated)


class TestEncodeBatch(unittest.TestCase):
    def test_batch_encode_multiple(self):
        batch = build_encode_batch("Straße HELLO")
        self.assertEqual(batch["count"], 2)
        self.assertEqual(batch["words"][0]["normalized"], "STRAßE")
        self.assertEqual(batch["words"][1]["normalized"], "HELLO")


if __name__ == "__main__":
    unittest.main()
