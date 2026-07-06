import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from analysis.binary.format import GpmFormatError, read_gpm
from analysis.binary.gpc import (
    decrypt_gpm_file,
    encrypt_gpm_file,
    is_encrypted_gpm_blob,
    peek_gpc_meta,
)
from analysis.compile.compiler import compile_text_to_gpm


class TestGpc(unittest.TestCase):
    def test_gpc_roundtrip(self):
        _, blob, _ = compile_text_to_gpm("Francesco Schauer")
        self.assertFalse(is_encrypted_gpm_blob(blob))

        enc_blob, enc = encrypt_gpm_file("Francesco Schauer", mode="word", keys_raw="GEHEIM")
        self.assertTrue(is_encrypted_gpm_blob(enc_blob))
        meta = peek_gpc_meta(enc_blob)
        self.assertEqual(meta["mode"], "word")

        dec = decrypt_gpm_file(enc_blob, keys_raw="GEHEIM")
        self.assertTrue(dec["gpc"])
        self.assertEqual(dec["text"], "Francesco Schauer")

    def test_read_gpm_rejects_gpc_without_key(self):
        enc_blob, _ = encrypt_gpm_file("Test", mode="word", keys_raw="KEY")
        with self.assertRaises(GpmFormatError):
            read_gpm(enc_blob)


if __name__ == "__main__":
    unittest.main()
