import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ge_prime.core import PRIME_MAP
from ge_prime.decode import decode_word
from ge_prime.encode import encode_word
from db.repository import WordRepository
from pipeline.normalize import denormalize_word, normalize_word
from pipeline.process import process_word


class TestAllLetters(unittest.TestCase):
    def test_single_letters_encode_decode(self):
        for letter in PRIME_MAP:
            substance, index = encode_word(letter)
            self.assertEqual(decode_word(substance, index), letter)

    def test_all_letters_in_word(self):
        word = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        substance, index = encode_word(word)
        self.assertEqual(decode_word(substance, index), word)

    def test_pdf_examples(self):
        for word in ("FRANCESCO", "SILVANO", "SCHAUER", "ROBOTERHEIT"):
            substance, index = encode_word(word)
            self.assertEqual(decode_word(substance, index), word)


class TestNormalization(unittest.TestCase):
    def test_umlaut_expansion(self):
        self.assertEqual(normalize_word("Straße"), "STRAßE")
        self.assertEqual(normalize_word("FRÄULEIN"), "FRAEULEIN")
        self.assertEqual(normalize_word("Müller"), "MUELLER")
        self.assertEqual(normalize_word("Größe"), "GROEßE")

    def test_eszett_is_own_letter(self):
        # ß bleibt erhalten und ist NICHT gleich ss
        self.assertEqual(normalize_word("Straße"), "STRAßE")
        self.assertEqual(normalize_word("Strasse"), "STRASSE")
        self.assertNotEqual(normalize_word("Straße"), normalize_word("Strasse"))

    def test_eszett_kept_uppercase(self):
        self.assertEqual(normalize_word("Strauß"), "STRAUß")
        self.assertEqual(normalize_word("ẞpaß"), "ßPAß")

    def test_eszett_has_own_prime(self):
        self.assertIn("ß", PRIME_MAP)
        substance, index = encode_word("STRAßE")
        self.assertEqual(decode_word(substance, index), "STRAßE")

    def test_eszett_step_lines(self):
        from pipeline.normalize import eszett_step_lines

        lines = eszett_step_lines("Straße", "STRAßE")
        self.assertEqual(len(lines), 1)
        self.assertIn("Primzahl 103", lines[0])
        self.assertIn("STRAßE", lines[0])
        self.assertEqual(eszett_step_lines("Strasse", "STRASSE"), [])
        self.assertEqual(eszett_step_lines("HALLO", "HALLO"), [])

    def test_denormalize_with_original(self):
        original = "FRÄULEIN"
        normalized = normalize_word(original)
        self.assertEqual(denormalize_word(normalized, original), original)

    def test_roundtrip_normalized_form(self):
        for word in ("Straße", "Müller", "Größe", "Über"):
            normalized = normalize_word(word)
            substance, index = encode_word(normalized)
            decoded = decode_word(substance, index)
            self.assertEqual(decoded, normalized)


class TestDatabaseStorage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "test.db"
        self.repo = WordRepository(self.db_path)
        self.repo.init_db()
        self.source_id = self.repo.get_or_create_source("test")

    def tearDown(self):
        self.repo.close()
        self.tmp.cleanup()

    def _store_and_load(self, word: str) -> dict:
        result = process_word(word, language="de", source="test")
        self.assertIsNotNone(result, f"process_word failed for {word!r}")
        self.repo.insert_words_batch([result], self.source_id)
        loaded = self.repo.get_by_original(word)
        self.assertIsNotNone(loaded)
        return {
            "word_original": loaded.word_original,
            "word_normalized": loaded.word_normalized,
            "substance": str(loaded.substance),
            "perm_index": loaded.perm_index,
        }

    def test_umlaut_original_preserved_in_db(self):
        for word in ("Straße", "FRÄULEIN", "Müller", "Größe"):
            row = self._store_and_load(word)
            self.assertEqual(row["word_original"], word)
            self.assertEqual(row["word_normalized"], normalize_word(word))

    def test_decode_from_db_matches_normalized(self):
        word = "Straße"
        row = self._store_and_load(word)
        decoded = decode_word(int(row["substance"]), row["perm_index"])
        self.assertEqual(decoded, row["word_normalized"])

    def test_display_from_db_matches_original(self):
        word = "Müller"
        row = self._store_and_load(word)
        display = denormalize_word(row["word_normalized"], row["word_original"])
        self.assertEqual(display, word)

    def test_load_via_repository_helper(self):
        word = "Größe"
        result = process_word(word, language="de", source="test")
        self.repo.insert_words_batch([result], self.source_id)
        loaded = self.repo.get_by_original(word)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.word_original, word)
        self.assertEqual(loaded.word_normalized, "GROEßE")
        self.assertEqual(loaded.decoded, "GROEßE")
        self.assertEqual(loaded.display, word)

    def test_substance_stored_as_text_and_loaded_as_int(self):
        word = "ROBOTERHEIT"
        result = process_word(word, language="de", source="test")
        self.repo.insert_words_batch([result], self.source_id)
        loaded = self.repo.get_by_original(word)
        self.assertIsNotNone(loaded)
        self.assertIsInstance(loaded.substance, int)
        self.assertEqual(loaded.decoded, word)

    def test_find_by_normalized_filters_language(self):
        w1 = process_word("Straße", language="de", source="test")
        w2 = process_word("Straße", language="random", source="web")
        self.repo.insert_words_batch([w1, w2], self.source_id)
        all_rows = self.repo.find_by_normalized("STRAßE")
        self.assertEqual(len(all_rows), 2)
        de_rows = self.repo.find_by_normalized("STRAßE", language="de")
        self.assertEqual(len(de_rows), 1)
        self.assertEqual(de_rows[0]["language"], "de")


class TestSanitizePreservesUmlauts(unittest.TestCase):
    def test_umlaut_words_not_rejected(self):
        for word in ("Straße", "Müller", "Größe", "FRÄULEIN"):
            result = process_word(word)
            self.assertIsNotNone(result, word)


class TestHeuristicDenormalize(unittest.TestCase):
    def test_without_original_returns_normalized_umlaut_form(self):
        # Ohne Original: AE/OE/UE werden zurueckgewandelt (AERO wird zu AER-Variante)
        self.assertEqual(denormalize_word("FRAEULEIN"), "FRÄULEIN")

    def test_literal_ae_sequences_are_ambiguous_without_original(self):
        # Bekannte Limitierung: ohne gespeichertes Original nicht eindeutig
        self.assertEqual(denormalize_word("AERO"), "ÄRO")


if __name__ == "__main__":
    unittest.main()
