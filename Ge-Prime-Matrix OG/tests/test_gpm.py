import base64
import io
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from gpm.compiler import compile_text
from gpm.format import GpmFormatError, VERSION, VERSION_V3, VERSION_V4, VERSION_V5, read_file_header_fields, read_gpm, write_gpm
from gpm.model import GpmDocument, GpmHeaderEntry, GpmToken
from gpm.reader import analyze_gpm, reconstruct_text, search_by_gcd, search_by_lcm, search_by_word
from pipeline.normalize import normalize_word
from web.app import app


def _build_v1_blob(header, body):
    """Erzeugt eine Legacy-v1-.gpm zum Testen der Lesekompatibilität."""
    blob = b"GPM\x01"
    blob += struct.pack("<BBIII", 1, 0, len(header), len(body), 0)
    for original, normalized, substance in header:
        o = original.encode("utf-8")
        n = normalized.encode("utf-8")
        s = substance.to_bytes((substance.bit_length() + 7) // 8 or 1, "big")
        blob += struct.pack("<H", len(o)) + o
        blob += struct.pack("<H", len(n)) + n
        blob += struct.pack("<H", len(s)) + s
    for word_id, perm in body:
        blob += struct.pack("<HI", word_id, perm)
    return blob


class TestGpmFormat(unittest.TestCase):
    def test_write_read_roundtrip(self):
        doc = GpmDocument(
            header=[
                GpmHeaderEntry(0, "straße", "STRAßE", 123456),
                GpmHeaderEntry(1, "hallo", "HALLO", 42),
            ],
            tokens=[GpmToken(0, 1, 0), GpmToken(1, 2, 1), GpmToken(0, 1, 2)],
            gaps=["", " ", " ", "!"],
            explicit=[],
        )
        blob = write_gpm(doc, version=VERSION_V5)
        self.assertEqual(blob[:4], b"GPM\x05")
        loaded = read_gpm(blob)
        self.assertEqual(len(loaded.header), 2)
        self.assertEqual(len(loaded.tokens), 3)
        self.assertEqual(loaded.header[0].word_normalized, "STRAßE")
        self.assertEqual(loaded.tokens[2].word_id, 0)
        self.assertEqual(loaded.tokens[1].case_code, 1)
        self.assertEqual(loaded.gaps, ["", " ", " ", "!"])

    def test_invalid_magic(self):
        with self.assertRaises(GpmFormatError):
            read_gpm(b"TXT\x02" + b"\x00" * 30)

    def test_crc_detects_corruption(self):
        _, blob, _ = compile_text("Hallo Welt")
        corrupted = bytearray(blob)
        corrupted[20] ^= 0xFF  # Byte im Payload kippen
        with self.assertRaises(GpmFormatError):
            read_gpm(bytes(corrupted))

    def test_gap_count_must_match(self):
        doc = GpmDocument(
            header=[GpmHeaderEntry(0, "a", "A", 3)],
            tokens=[GpmToken(0, 1, 0)],
            gaps=["only-one"],  # erwartet werden 2
            explicit=[],
        )
        with self.assertRaises(GpmFormatError):
            write_gpm(doc)


class TestGpmCompiler(unittest.TestCase):
    def test_exact_reconstruction_with_punctuation(self):
        text = "Hallo, Welt! Test 123 — fertig.\nNeue Zeile."
        _, blob, stats = compile_text(text)
        self.assertTrue(stats.lossless)
        self.assertEqual(reconstruct_text(read_gpm(blob)), text)

    def test_eszett_and_ss_are_distinct(self):
        text = "Straße Strasse"
        doc, _, stats = compile_text(text)
        self.assertEqual(stats.unique_words, 2)
        normals = {e.word_normalized for e in doc.header}
        self.assertIn("STRAßE", normals)
        self.assertIn("STRASSE", normals)

    def test_case_layer_three_states(self):
        text = "haus Haus HAUS"
        doc, blob, stats = compile_text(text)
        # gleiche Buchstaben → ein Genom-Eintrag, drei Schreibweisen
        self.assertEqual(stats.unique_words, 1)
        codes = [t.case_code for t in doc.tokens]
        self.assertEqual(codes, [0, 1, 2])
        self.assertEqual(reconstruct_text(read_gpm(blob)), text)

    def test_mixed_case_uses_explicit_overflow(self):
        text = "McDonald"
        doc, blob, stats = compile_text(text)
        self.assertTrue(any(idx == 0 for idx, _ in doc.explicit))
        self.assertEqual(reconstruct_text(read_gpm(blob)), text)

    def test_unique_header_for_repeated_words(self):
        text = "HALLO HALLO WELT HALLO"
        doc, blob, stats = compile_text(text)
        self.assertEqual(stats.unique_words, 2)
        self.assertEqual(stats.total_tokens, 4)
        self.assertEqual(reconstruct_text(read_gpm(blob)), text)

    def test_emoji_and_digits_preserved(self):
        text = "Preis: 99€ super 🎉"
        _, blob, stats = compile_text(text)
        self.assertTrue(stats.lossless)
        self.assertEqual(reconstruct_text(read_gpm(blob)), text)
        self.assertEqual(stats.separator_perm, 1 | 2 | 4)

    def test_v4_perm_zero_for_simple_text(self):
        _, blob, stats = compile_text("Hallo Welt")
        self.assertEqual(stats.separator_perm, 0)
        self.assertLess(stats.separator_bytes, 10)
        self.assertLess(stats.file_bytes, 130)

    def test_v6_cell_body_for_two_tokens(self):
        """v6 Zell-Body + Structural-Index für zwei eindeutige Wörter."""
        doc, _, stats = compile_text("Hallo Welt")
        self.assertEqual(stats.total_tokens, 2)
        self.assertEqual(stats.body_mode, "cell")
        self.assertEqual(stats.zellen_anzahl, 1)
        self.assertGreaterEqual(stats.body_bytes, 39)

    def test_v4_smaller_separator_than_v2_style(self):
        """Separator-Layer v3 deutlich kleiner als altes u32-Gap-Modell."""
        _, _, stats = compile_text("Hallo Welt")
        old_style = sum(4 + len(g.encode("utf-8")) for g in ["", " ", ""])
        self.assertLess(stats.separator_bytes, old_style)

    def test_read_file_header_fields_v7(self):
        _, blob, stats = compile_text("Hallo Welt")
        ver, perm, middle_len = read_file_header_fields(blob)
        self.assertEqual(ver, 7)
        self.assertEqual(perm, 0)
        self.assertEqual(middle_len, stats.separator_bytes)

    def test_v4_long_word_perm_space_roundtrip(self):
        """13 verschiedene Buchstaben → N > 2³²; v4 speichert I in 8 Byte."""
        word = "ABCDEFGHIJKLM"
        _, blob, stats = compile_text(word)
        self.assertTrue(stats.lossless)
        self.assertEqual(reconstruct_text(read_gpm(blob)), word)
        analysis = analyze_gpm(blob)
        self.assertEqual(analysis.version, 7)
        self.assertGreaterEqual(analysis.body_bytes, 11)


class TestGpmReader(unittest.TestCase):
    def setUp(self):
        _, self.blob, _ = compile_text("Francesco Francesco Schauer Straße")

    def test_search_exact_substance(self):
        doc = read_gpm(self.blob)
        hit = search_by_word(doc, "Francesco")
        self.assertTrue(hit["found_in_header"])
        self.assertEqual(hit["occurrences"], 2)

    def test_search_missing_word(self):
        doc = read_gpm(self.blob)
        hit = search_by_word(doc, "XYZABC")
        self.assertFalse(hit["found_in_header"])

    def test_gcd_filter_finds_shared_letters(self):
        doc = read_gpm(self.blob)
        result = search_by_gcd(doc, "Straße")
        self.assertGreaterEqual(result["unique_words"], 1)

    def test_lcm_filter_finds_union_cover(self):
        _, blob, _ = compile_text("MUTWUT MUT WUT")
        doc = read_gpm(blob)
        result = search_by_lcm(doc, "MUT", "WUT")
        originals = {m["original"] for m in result["matches"]}
        self.assertIn("mutwut", originals)
        self.assertNotIn("mut", originals)
        self.assertNotIn("wut", originals)
        self.assertEqual(set(result["union_letters"].keys()), {"M", "U", "T", "W"})

    def test_analyze_structure(self):
        analysis = analyze_gpm(self.blob)
        self.assertEqual(analysis.version, 7)
        self.assertTrue(analysis.lossless)
        self.assertGreater(analysis.header_bytes, 0)
        self.assertGreater(analysis.body_bytes, 0)
        self.assertIn("Francesco", analysis.reconstructed_text)


def _build_v3_blob(header, body, gaps):
    """Legacy-v3-.gpm für Lesekompatibilitätstests."""
    import zlib

    from gpm.separator_codec import encode_gaps, scan_perm_code

    document = GpmDocument(
        header=[
            GpmHeaderEntry(i, o, n, s) for i, (o, n, s) in enumerate(header)
        ],
        tokens=[GpmToken(wid, perm, 0) for wid, perm in body],
        gaps=gaps,
        explicit=[],
    )
    perm = scan_perm_code(gaps)
    separator_blob = encode_gaps(gaps, perm)
    genome = bytearray()
    for entry in document.header:
        original = entry.word_original.encode("utf-8")
        normalized = entry.word_normalized.encode("utf-8")
        substance = entry.substance.to_bytes(
            (entry.substance.bit_length() + 7) // 8 or 1, "big"
        )
        genome += struct.pack("<H", len(original)) + original
        genome += struct.pack("<H", len(normalized)) + normalized
        genome += struct.pack("<H", len(substance)) + substance
    body_bytes = bytearray()
    for token in document.tokens:
        body_bytes += struct.pack(
            "<HIB", token.word_id, token.perm_index, token.case_code
        )
    payload = bytes(genome) + bytes(body_bytes) + separator_blob
    file_header = b"GPM" + struct.pack(
        "<BBIIIIII",
        VERSION_V3,
        0,
        len(document.header),
        len(document.tokens),
        perm,
        0,
        len(separator_blob),
        len(payload),
    )
    blob = file_header + payload
    crc = zlib.crc32(blob) & 0xFFFFFFFF
    return blob + struct.pack("<I", crc)


class TestGpmLegacyV3(unittest.TestCase):
    def test_read_v3_blob(self):
        blob = _build_v3_blob(
            header=[("hallo", "HALLO", 372945), ("welt", "WELT", 123)],
            body=[(0, 1), (1, 1)],
            gaps=["", " ", ""],
        )
        doc = read_gpm(blob)
        self.assertEqual(len(doc.header), 2)
        self.assertEqual(reconstruct_text(doc), "hallo welt")
        analysis = analyze_gpm(blob)
        self.assertEqual(analysis.version, 3)
        self.assertTrue(analysis.lossless)


class TestGpmLegacyV1(unittest.TestCase):
    def test_read_v1_blob(self):
        blob = _build_v1_blob(
            header=[("Hallo", "HALLO", 1), ("Welt", "WELT", 2)],
            body=[(0, 1), (1, 1)],
        )
        doc = read_gpm(blob)
        self.assertEqual(len(doc.header), 2)
        self.assertEqual(len(doc.tokens), 2)
        # v1 wird mit Leerzeichen rekonstruiert
        self.assertEqual(reconstruct_text(doc), "Hallo Welt")

    def test_analyze_v1_marks_not_lossless(self):
        blob = _build_v1_blob(header=[("Test", "TEST", 7)], body=[(0, 1)])
        analysis = analyze_gpm(blob)
        self.assertEqual(analysis.version, 1)
        self.assertFalse(analysis.lossless)


class TestGpmApi(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True

    def test_compile_api(self):
        with app.test_client() as client:
            resp = client.post(
                "/api/gpm/compile",
                json={"text": "HALLO WELT Straße"},
            )
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertIn("file_base64", data)
            self.assertEqual(data["gpm_version"], 7)
            self.assertEqual(data["stats"]["gpm_version"], 7)
            self.assertIn("si_storage", data["stats"])
            self.assertIn("I_Satz", data["stats"]["si_storage"]["summary"])
            self.assertEqual(data["stats"]["unique_words"], 3)
            self.assertTrue(data["lossless"])
            blob = base64.b64decode(data["file_base64"])
            self.assertEqual(blob[:4], b"GPM\x07")

    def test_read_api_roundtrip(self):
        with app.test_client() as client:
            compiled = client.post(
                "/api/gpm/compile",
                json={"text": "Test, Wort! 7"},
            ).get_json()
            resp = client.post(
                "/api/gpm/read",
                json={"file_base64": compiled["file_base64"]},
            )
            self.assertEqual(resp.status_code, 200)
            analysis = resp.get_json()["analysis"]
            self.assertEqual(analysis["gpm_version"], 7)
            self.assertIn("si_storage", analysis)
            self.assertEqual(analysis["si_storage"]["gpm_version"], 7)
            self.assertEqual(analysis["total_tokens"], 2)
            self.assertEqual(analysis["reconstructed_text"], "Test, Wort! 7")
            self.assertTrue(analysis["lossless"])

    def test_search_api(self):
        with app.test_client() as client:
            compiled = client.post(
                "/api/gpm/compile",
                json={"text": "Alpha Beta Alpha"},
            ).get_json()
            resp = client.post(
                "/api/gpm/search",
                json={
                    "file_base64": compiled["file_base64"],
                    "query": "Alpha",
                    "mode": "substance",
                },
            )
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.get_json()["result"]["occurrences"], 2)

    def test_search_api_lcm(self):
        with app.test_client() as client:
            compiled = client.post(
                "/api/gpm/compile",
                json={"text": "MUTWUT MUT WUT"},
            ).get_json()
            resp = client.post(
                "/api/gpm/search",
                json={
                    "file_base64": compiled["file_base64"],
                    "query": "MUT",
                    "query2": "WUT",
                    "mode": "lcm",
                },
            )
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertEqual(data["mode"], "lcm")
            originals = {m["original"] for m in data["result"]["matches"]}
            self.assertIn("mutwut", originals)


class TestGpmEncrypted(unittest.TestCase):
    TEXT = "Geheimer Text für die Klinik."

    def test_gpc_roundtrip(self):
        from gpm.cipher_wrap import decrypt_gpm_file, encrypt_gpm_file, is_encrypted_gpm_blob, peek_gpc_meta

        blob, enc = encrypt_gpm_file(self.TEXT, mode="si", keys_raw="SCHLUESSEL")
        self.assertTrue(is_encrypted_gpm_blob(blob))
        meta = peek_gpc_meta(blob)
        self.assertEqual(meta["mode"], "si")
        dec = decrypt_gpm_file(blob, keys_raw="SCHLUESSEL")
        self.assertEqual(dec["text"], self.TEXT)

    def test_compile_api_encrypted(self):
        with app.test_client() as client:
            resp = client.post(
                "/api/gpm/compile",
                json={
                    "text": self.TEXT,
                    "encrypt": True,
                    "cipher_mode": "word",
                    "cipher_keys": "GEHEIM",
                },
            )
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertTrue(data["encrypted"])
            self.assertEqual(data["header_preview"], [])

    def test_read_encrypted_needs_keys(self):
        from gpm.cipher_wrap import encrypt_gpm_file

        blob, _ = encrypt_gpm_file(self.TEXT, mode="word", keys_raw="GEHEIM")
        with app.test_client() as client:
            resp = client.post(
                "/api/gpm/read",
                data={"file": (io.BytesIO(blob), "secret.gpm")},
                content_type="multipart/form-data",
            )
            self.assertEqual(resp.status_code, 400)
            data = resp.get_json()
            self.assertTrue(data.get("needs_keys"))

    def test_read_encrypted_with_keys(self):
        from gpm.cipher_wrap import encrypt_gpm_file

        blob, _ = encrypt_gpm_file(self.TEXT, mode="word", keys_raw="GEHEIM")
        with app.test_client() as client:
            resp = client.post(
                "/api/gpm/read",
                data={
                    "file": (io.BytesIO(blob), "secret.gpm"),
                    "cipher_keys": "GEHEIM",
                },
                content_type="multipart/form-data",
            )
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertTrue(data.get("encrypted_source"))
            self.assertEqual(data["analysis"]["reconstructed_text"], self.TEXT)


if __name__ == "__main__":
    unittest.main()
