import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from analysis.security.cipher import (
    MODE_HARDCORE,
    MODE_PRIME,
    MODE_SI,
    MODE_WORD,
    assess_security,
    decrypt_ciphertext,
    encrypt_text,
    parse_key_token,
)


class TestCipher(unittest.TestCase):
    SAMPLE = "Der schnelle Fuchs springt. Hallo Welt!"

    def test_roundtrip_word_mode(self):
        enc = encrypt_text(self.SAMPLE, mode=MODE_WORD, keys_raw="GEHEIM")
        dec = decrypt_ciphertext(enc["ciphertext"], keys_raw="GEHEIM")
        self.assertEqual(dec["text"], self.SAMPLE)
        self.assertEqual(enc["security"]["level"], "niedrig")

    def test_roundtrip_prime_mode(self):
        enc = encrypt_text("Alpha Beta", mode=MODE_PRIME, keys_raw="prime:17")
        dec = decrypt_ciphertext(enc["ciphertext"], keys_raw="prime:17")
        self.assertEqual(dec["text"], "Alpha Beta")

    def test_roundtrip_si_mode(self):
        enc = encrypt_text(self.SAMPLE, mode=MODE_SI, keys_raw="SCHLUESSEL")
        dec = decrypt_ciphertext(enc["ciphertext"], keys_raw="SCHLUESSEL")
        self.assertEqual(dec["text"], self.SAMPLE)
        self.assertGreaterEqual(enc["security"]["score"], 55)

    def test_roundtrip_hardcore_mixed_keys(self):
        keys = "GEHEIM, prime:19, ALPHA, prime:103"
        enc = encrypt_text(self.SAMPLE, mode=MODE_HARDCORE, keys_raw=keys)
        dec = decrypt_ciphertext(enc["ciphertext"], keys_raw=keys)
        self.assertEqual(dec["text"], self.SAMPLE)
        self.assertGreaterEqual(enc["security"]["score"], 72)

    def test_wrong_key_fails(self):
        enc = encrypt_text("Test", mode=MODE_WORD, keys_raw="Richtig")
        with self.assertRaises(ValueError):
            decrypt_ciphertext(enc["ciphertext"], keys_raw="Falsch")

    def test_parse_prime_key(self):
        entry = parse_key_token("prime:103")
        self.assertEqual(entry.kind, "prime")
        self.assertEqual(entry.value, "103")

    def test_assess_security_hardcore_bonus(self):
        sec = assess_security(
            MODE_HARDCORE,
            [parse_key_token("A"), parse_key_token("B"), parse_key_token("prime:17")],
        )
        self.assertGreater(sec["score"], 72)


if __name__ == "__main__":
    unittest.main()
