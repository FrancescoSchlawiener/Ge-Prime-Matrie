import base64
import io
import sys
import tempfile
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import web.app as web_app
from web.app import app
from ge_prime.config import REQUIRED_API_ROUTES
from db.repository import WordRepository


class TestWebThreadSafety(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        WordRepository().init_db()

    def test_homepage_under_concurrent_requests(self):
        errors: list[str] = []

        def hit_home():
            try:
                with app.test_client() as client:
                    resp = client.get("/")
                    if resp.status_code != 200:
                        errors.append(f"status {resp.status_code}")
            except Exception as exc:
                errors.append(str(exc))

        threads = [threading.Thread(target=hit_home) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(errors, [])

    def test_encode_api_returns_steps(self):
        with app.test_client() as client:
            resp = client.post("/api/encode", json={"text": "HALLO WELT"})
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertEqual(data["count"], 2)
            self.assertEqual(len(data["words"][0]["steps"]), 4)
            self.assertEqual(data["words"][0]["normalized"], "HALLO")
            self.assertEqual(data["words"][1]["normalized"], "WELT")
            self.assertEqual(data["language"], "Random / unsortiert")
            self.assertEqual(data["words"][0]["language"], "random")

    def test_encode_api_tags_german_sentence(self):
        with app.test_client() as client:
            resp = client.post(
                "/api/encode",
                json={"text": "Der Patient erhält Diagnose und Therapie."},
            )
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertEqual(data["language"], "Deutsch")
            self.assertEqual(data["words"][0]["language"], "de")

    def test_encode_api_ignores_punctuation(self):
        with app.test_client() as client:
            resp = client.post("/api/encode", json={"text": "Hallo, Welt!"})
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertEqual(data["count"], 2)

    def test_encode_api_persists_to_db(self):
        tmp = tempfile.TemporaryDirectory()
        db_path = Path(tmp.name) / "encode_test.db"
        test_repo = WordRepository(db_path)
        test_repo.init_db()
        old_repo = web_app.repo
        web_app.repo = test_repo
        try:
            with app.test_client() as client:
                before = test_repo.total_count()
                resp = client.post("/api/encode", json={"text": "NeuInDbXYZ"})
                self.assertEqual(resp.status_code, 200)
                data = resp.get_json()
                self.assertEqual(data["saved"], 1)
                self.assertEqual(data["db_duplicates"], 0)
                self.assertEqual(data["db_total"], before + 1)
                self.assertEqual(test_repo.total_count(), before + 1)
                row = test_repo.get_by_original("NeuInDbXYZ")
                self.assertIsNotNone(row)
                self.assertEqual(row.word_normalized, "NEUINDBXYZ")
                self.assertEqual(row.language, "random")

                resp2 = client.post("/api/encode", json={"text": "NeuInDbXYZ"})
                data2 = resp2.get_json()
                self.assertEqual(data2["saved"], 0)
                self.assertEqual(data2["db_duplicates"], 1)
                self.assertEqual(test_repo.total_count(), before + 1)
        finally:
            web_app.repo = old_repo
            test_repo.close()
            tmp.cleanup()

    def test_db_stats_api(self):
        with app.test_client() as client:
            resp = client.get("/api/db/stats")
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertIn("total_words", data)
            self.assertIn("lang_stats", data)
            self.assertIsInstance(data["lang_stats"], list)

    def test_favicon_route(self):
        with app.test_client() as client:
            resp = client.get("/favicon.ico")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("image/svg", resp.content_type)
            self.assertIn(b"<svg", resp.data)

    def test_health_api(self):
        with app.test_client() as client:
            resp = client.get("/api/health")
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertTrue(data["ok"])
            self.assertEqual(data["version"], "2026.06-gpm-v49")
            self.assertEqual(data["gpm_version"], 7)
            self.assertTrue(data["routes"]["db_stats"])
            self.assertTrue(data["routes"]["encode"])
            self.assertTrue(data["routes"]["size_encode_word"])
            self.assertTrue(data["routes"]["size_gpm"])
            self.assertEqual(len(data["routes"]), len(REQUIRED_API_ROUTES))
            self.assertIn("db_path", data)
            self.assertIn("db_words", data)

    def test_version_api(self):
        with app.test_client() as client:
            resp = client.get("/api/version")
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertEqual(data["version"], "2026.06-gpm-v49")
            self.assertEqual(data["gpm_version"], 7)

    def test_decode_api_roundtrip(self):
        with app.test_client() as client:
            enc = client.post("/api/encode", json={"text": "WELT"})
            enc_data = enc.get_json()
            word = enc_data["words"][0]
            dec = client.post(
                "/api/decode",
                json={
                    "substance": word["substance"],
                    "perm_index": word["perm_index"],
                },
            )
            self.assertEqual(dec.status_code, 200)
            dec_data = dec.get_json()
            self.assertEqual(dec_data["word"], "WELT")
            self.assertGreaterEqual(len(dec_data["steps"]), 4)

    def test_compare_api_eszett_vs_ss(self):
        with app.test_client() as client:
            resp = client.post(
                "/api/compare",
                json={"word1": "Straße", "word2": "Strasse"},
            )
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertEqual(data["word1"]["normalized"], "STRAßE")
            self.assertEqual(data["word2"]["normalized"], "STRASSE")
            self.assertNotEqual(data["word1"]["substance"], data["word2"]["substance"])
            notes = data["comparison"]["notes"]
            self.assertTrue(any("Straße" in n or "STRAßE" in n or "ß" in n for n in notes))

    def test_compare_api_includes_lcm(self):
        with app.test_client() as client:
            resp = client.post(
                "/api/compare",
                json={"word1": "MUT", "word2": "WUT"},
            )
            self.assertEqual(resp.status_code, 200)
            cmp = resp.get_json()["comparison"]
            self.assertIn("lcm_value", cmp)
            self.assertEqual(set(cmp["union_letters"].keys()), {"M", "U", "T", "W"})

    def test_diff_api_anagram(self):
        with app.test_client() as client:
            resp = client.post(
                "/api/diff",
                json={"word1": "LISTEN", "word2": "SILENT"},
            )
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            diff = data["diff"]
            self.assertTrue(diff["is_anagram"])
            self.assertTrue(diff["is_same_substance"])
            self.assertFalse(diff["is_subset_1_in_2"])
            self.assertTrue(diff["same_length"])
            self.assertIn("remainder_s1", diff)
            self.assertIn("notes", diff)

    def test_diff_api_subset_at_cat(self):
        with app.test_client() as client:
            resp = client.post(
                "/api/diff",
                json={"word1": "AT", "word2": "CAT"},
            )
            self.assertEqual(resp.status_code, 200)
            diff = resp.get_json()["diff"]
            self.assertEqual(diff["remainder_s1"], 1)
            self.assertTrue(diff["is_subset_1_in_2"])
            self.assertFalse(diff["is_subset_2_in_1"])
            self.assertGreater(diff["remainder_s2"], 1)

    def test_icurve_api_identical_texts(self):
        text = "Der schnelle braune Fuchs springt."
        with app.test_client() as client:
            resp = client.post(
                "/api/i-curve",
                json={"text_a": text, "text_b": text, "source_a": "text", "source_b": "text"},
            )
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertIn("curve_a", data)
            self.assertIn("curve_b", data)
            self.assertIn("cell_geometry_a", data)
            self.assertIn("cell_comparison", data)
            c = data["comparison"]
            self.assertAlmostEqual(c["geometry_score"], 1.0, places=3)
            self.assertAlmostEqual(c["literal_match_ratio"], 1.0, places=3)
            self.assertTrue(c["aligned"])
            self.assertIn("interpretation", c)
            self.assertIn("notes", c)
            self.assertIn("structural_cell_twins", c)
            self.assertGreater(data["cell_geometry_a"]["summary"]["cell_count"], 0)
            self.assertIn("substance_comparison", data)
            self.assertIn("relation_comparison", data)
            self.assertIn("cross_analysis_a", data)
            self.assertIn("cross_analysis_b", data)
            self.assertIn("meta_comparison", data)
            self.assertIn("hierarchy_comparison", data)
            self.assertIn("enjambement_profile", data["cross_analysis_a"])
            self.assertIn("viewport_a", data)
            self.assertIn("viewport_b", data)
            self.assertIn("plain_gpm_base64", data["viewport_a"])
            self.assertIn("token_char_map", data["viewport_a"])
            self.assertIn("structural_lines", data["viewport_a"])
            self.assertIn("reconstructed_text", data["viewport_a"])
            self.assertIn("substance_score", data["structure_assessment"])
            self.assertTrue(c["fester_offset_erkannt"])
            self.assertEqual(data["structure_assessment"].get("db_audit_mode"), "de_en")
            self.assertIn("validation_pipeline", data)
            hc = data["hierarchy_comparison"]["semantic"]
            self.assertIn("phrase", hc)
            self.assertIn("paragraph", hc)
            self.assertIn("sentence", hc)
            self.assertIn("geometry_score", hc["phrase"])
            self.assertIn("geometry_score", hc["paragraph"])
            struct_hc = data["hierarchy_comparison"]["structural"]
            self.assertIn("line", struct_hc)
            self.assertNotIn("page", struct_hc)
            self.assertNotIn("pages", data.get("structural_a", {}))
            self.assertIn("lines", data["structural_a"])
            self.assertIn("sparkline_points", data["curve_a"])
            self.assertIn("points", data["curve_a"])
            self.assertIn("point_count", data["curve_a"])
            self.assertFalse(data["curve_a"]["sparkline_downsampled"])

    def test_icurve_api_long_text_sparkline_downsample(self):
        text = " ".join(f"wort{i}" for i in range(1500))
        with app.test_client() as client:
            resp = client.post(
                "/api/i-curve",
                json={"text_a": text, "text_b": text, "source_a": "text", "source_b": "text"},
            )
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            curve = data["curve_a"]
            self.assertGreater(curve["point_count"], 500)
            self.assertLessEqual(len(curve["points"]), 31)
            self.assertLessEqual(len(curve["sparkline_points"]), 502)
            self.assertTrue(curve["sparkline_downsampled"])
            self.assertTrue(curve["points_truncated"])
            self.assertEqual(curve["sparkline_points"][0], curve["points"][0])
            self.assertEqual(curve["sparkline_points"][-1], curve["points"][-1])
            self.assertEqual(curve["sparkline_points"][-1]["position"], curve["point_count"] - 1)

    def test_icurve_api_paragraph_level_crlf(self):
        text = "Erster Absatz.\r\n\r\nZweiter Absatz mit Text.\r\nNoch eine Zeile."
        with app.test_client() as client:
            resp = client.post(
                "/api/i-curve",
                json={"text_a": text, "text_b": text, "source_a": "text", "source_b": "text"},
            )
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            para_a = data["semantic_a"]["paragraphs"]
            self.assertEqual(para_a["point_count"], 2)
            self.assertEqual(len(para_a["sparkline_points"]), 2)
            self.assertIn("i_absatz_ratio", para_a["sparkline_points"][0])
            self.assertIn("paragraph_index", para_a["sparkline_points"][0])
            hc = data["hierarchy_comparison"]["semantic"]["paragraph"]
            self.assertFalse(hc.get("dtw_failed", True))
            self.assertIn("geometry_score", hc)

    def test_icurve_api_db_audit_mode(self):
        text = "Der schnelle braune Fuchs springt."
        with app.test_client() as client:
            off = client.post(
                "/api/i-curve",
                json={
                    "text_a": text,
                    "text_b": text,
                    "source_a": "text",
                    "source_b": "text",
                    "db_audit_mode": "off",
                },
            )
            self.assertEqual(off.status_code, 200)
            off_data = off.get_json()
            self.assertEqual(off_data["structure_assessment"]["db_audit_mode"], "off")
            lang = off_data["meta_a"]["language"]
            if lang.get("code") in ("de", "en"):
                self.assertFalse(lang["db_coverage"]["available"])
            bad = client.post(
                "/api/i-curve",
                json={
                    "text_a": text,
                    "text_b": text,
                    "source_a": "text",
                    "source_b": "text",
                    "db_audit_mode": "invalid",
                },
            )
            self.assertEqual(bad.status_code, 400)

    def test_gpm_compile_includes_cell_geometry(self):
        text = "Der schnelle Fuchs springt. Er rennt weiter."
        with app.test_client() as client:
            resp = client.post("/api/gpm/compile", json={"text": text})
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertIn("cell_geometry", data)
            self.assertGreater(data["cell_geometry"]["count"], 0)
            self.assertIn("points", data["cell_geometry"])
            self.assertEqual(data["stats"]["body_mode"], "cell")

    def test_icurve_api_gpm_roundtrip(self):
        text = "Hallo Welt Test"
        with app.test_client() as client:
            compile_resp = client.post("/api/gpm/compile", json={"text": text})
            self.assertEqual(compile_resp.status_code, 200)
            b64 = compile_resp.get_json()["file_base64"]
            resp = client.post(
                "/api/i-curve",
                json={
                    "text_a": text,
                    "source_a": "text",
                    "file_b_base64": b64,
                    "source_b": "gpm",
                },
            )
            self.assertEqual(resp.status_code, 200)
            c = resp.get_json()["comparison"]
            self.assertAlmostEqual(c["geometry_score"], 1.0, places=3)

    def test_icurve_api_gpm_multipart_upload(self):
        text = "Hallo Welt Test"
        with app.test_client() as client:
            compile_resp = client.post("/api/gpm/compile", json={"text": text})
            self.assertEqual(compile_resp.status_code, 200)
            blob = base64.b64decode(compile_resp.get_json()["file_base64"])
            resp = client.post(
                "/api/i-curve",
                data={
                    "text_a": text,
                    "source_a": "text",
                    "source_b": "gpm",
                    "db_audit_mode": "off",
                    "file_b": (io.BytesIO(blob), "test.gpm"),
                },
                content_type="multipart/form-data",
            )
            self.assertEqual(resp.status_code, 200)
            c = resp.get_json()["comparison"]
            self.assertAlmostEqual(c["geometry_score"], 1.0, places=3)

    def test_gpm_compile_encrypted_returns_plain_for_memory(self):
        text = "Geheimnisvoller Text für I-Kurve"
        with app.test_client() as client:
            resp = client.post(
                "/api/gpm/compile",
                json={
                    "text": text,
                    "encrypt": True,
                    "cipher_mode": "word",
                    "cipher_keys": "TESTKEY",
                },
            )
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertTrue(data["encrypted"])
            self.assertIn("plain_file_base64", data)
            self.assertNotEqual(data["file_base64"], data["plain_file_base64"])
            icurve = client.post(
                "/api/i-curve",
                json={
                    "text_a": text,
                    "source_a": "text",
                    "file_b_base64": data["plain_file_base64"],
                    "source_b": "gpm",
                },
            )
            self.assertEqual(icurve.status_code, 200)
            self.assertAlmostEqual(icurve.get_json()["comparison"]["geometry_score"], 1.0, places=3)
            bad = client.post(
                "/api/i-curve",
                json={
                    "text_a": text,
                    "source_a": "text",
                    "file_b_base64": data["file_base64"],
                    "source_b": "gpm",
                },
            )
            self.assertEqual(bad.status_code, 400)
            self.assertIn("Verschlüsselte", bad.get_json()["error"])

    def test_icurve_api_includes_meta_genome(self):
        with app.test_client() as client:
            resp = client.post(
                "/api/i-curve",
                json={
                    "text_a": "Der Patient erhält Diagnose und Therapie in der Klinik.",
                    "text_b": "Der Patient erhält Diagnose und Therapie in der Klinik.",
                    "source_a": "text",
                    "source_b": "text",
                },
            )
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertIn("meta_a", data)
            self.assertIn("meta_comparison", data)
            self.assertIn("structure_assessment", data)
            self.assertNotIn("plagiarism_assessment", data)
            lang = data["meta_a"]["language"]
            dom = data["meta_a"]["domain"]
            self.assertIn("code", lang)
            self.assertIn("method", lang)
            self.assertIn("confidence", lang)
            self.assertIn("code", dom)
            self.assertIn("fallback", dom)
            self.assertIn("matched_keywords", dom)
            self.assertEqual(lang["code"], "de")
            self.assertEqual(dom["code"], "medical")
            notes = data["comparison"].get("notes") or []
            self.assertTrue(any("Funktionswort" in n or "Referenz-Profil" in n for n in notes))

    def test_icurve_api_missing_source(self):
        with app.test_client() as client:
            resp = client.post(
                "/api/i-curve",
                json={"text_a": "Hallo", "source_a": "text"},
            )
            self.assertEqual(resp.status_code, 400)

    def test_icurve_api_large_text_avoids_int_str_limit(self):
        text = ("Patient Diagnose Therapie Symptom Operation Klinik Arzt Behandlung " * 60).strip()
        with app.test_client() as client:
            resp = client.post(
                "/api/i-curve",
                json={
                    "text_a": text,
                    "text_b": text,
                    "source_a": "text",
                    "source_b": "text",
                },
            )
            self.assertEqual(resp.status_code, 200, resp.get_json())
            data = resp.get_json()
            self.assertAlmostEqual(data["comparison"]["geometry_score"], 1.0, places=3)
            self.assertIn("meta_comparison", data)

    def test_icurve_api_nfd_text_matches_nfc_reference(self):
        nfc = "Gr\u00e4ser wachsen."
        nfd = "Gr\u0061\u0308ser wachsen."
        with app.test_client() as client:
            nfc_resp = client.post(
                "/api/i-curve",
                json={"text_a": nfc, "text_b": nfc, "source_a": "text", "source_b": "text"},
            )
            nfd_resp = client.post(
                "/api/i-curve",
                json={"text_a": nfd, "text_b": nfd, "source_a": "text", "source_b": "text"},
            )
            self.assertEqual(nfc_resp.status_code, 200)
            self.assertEqual(nfd_resp.status_code, 200)
            nfc_data = nfc_resp.get_json()
            nfd_data = nfd_resp.get_json()
            self.assertAlmostEqual(
                nfd_data["comparison"]["geometry_score"],
                nfc_data["comparison"]["geometry_score"],
                places=3,
            )

    def test_icurve_api_relation_spans_and_compressed_breaks(self):
        text = "Patient Diagnose Therapie Symptom Operation Klinik Arzt Behandlung."
        with app.test_client() as client:
            resp = client.post(
                "/api/i-curve",
                json={"text_a": text, "text_b": text, "source_a": "text", "source_b": "text"},
            )
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            rel = data["relation_comparison"]
            self.assertIn("shared_bigram_spans", rel)
            self.assertIn("shared_word_bigrams", rel)
            breaks = data["cross_analysis_a"].get("rhythm_breaks") or []
            for row in breaks:
                self.assertNotIn("inter_start", row)
                self.assertNotIn("inter_end", row)

    def test_spectroscope_api_crlf_selection_spans_paragraph_gap(self):
        text = "Erster Absatz.\r\n\r\nZweiter Absatz mit Text."
        normalized = text.replace("\r\n", "\n")
        with app.test_client() as client:
            resp = client.post(
                "/api/spectroscope",
                json={
                    "source": "text",
                    "text": text,
                    "selection_start": 0,
                    "selection_end": len(normalized),
                    "modes": ["structural_twin"],
                },
            )
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertIn("token_char_map", data)
            self.assertGreater(len(data["token_char_map"]), 0)
            from ge_prime.hierarchy import build_document_hierarchy
            from gpm.compiler import compile_text

            doc, _, _ = compile_text(normalized)
            self.assertEqual(len(build_document_hierarchy(doc).semantic.paragraphs), 2)

    def test_spectroscope_api_compressed_matches(self):
        text = "Alpha Beta Gamma Delta."
        with app.test_client() as client:
            resp = client.post(
                "/api/spectroscope",
                json={
                    "source": "text",
                    "text": text,
                    "selection_start": 0,
                    "selection_end": len(text),
                    "modes": ["anagram_shadow"],
                },
            )
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertIn("token_char_map", data)
            for match in data.get("matches") or []:
                self.assertIn("token_start", match)
                self.assertIn("token_count", match)
                self.assertNotIn("char_start", match)

    def test_cipher_encrypt_decrypt_roundtrip(self):
        text = "Hallo Welt — Geheim!"
        with app.test_client() as client:
            enc = client.post(
                "/api/cipher/encrypt",
                json={"text": text, "mode": "si", "keys": "SCHLUESSEL"},
            )
            self.assertEqual(enc.status_code, 200)
            payload = enc.get_json()
            self.assertIn("ciphertext", payload)
            self.assertIn("security", payload)
            self.assertGreaterEqual(payload["security"]["score"], 55)
            dec = client.post(
                "/api/cipher/decrypt",
                json={"ciphertext": payload["ciphertext"], "keys": "SCHLUESSEL"},
            )
            self.assertEqual(dec.status_code, 200)
            self.assertEqual(dec.get_json()["text"], text)

    def test_cipher_hardcore_encrypt(self):
        with app.test_client() as client:
            resp = client.post(
                "/api/cipher/encrypt",
                json={
                    "text": "Alpha Beta Gamma",
                    "mode": "hardcore",
                    "keys": "A, prime:17, B, prime:19",
                },
            )
            self.assertEqual(resp.status_code, 200)
            self.assertGreaterEqual(resp.get_json()["security"]["score"], 72)


if __name__ == "__main__":
    unittest.main()
