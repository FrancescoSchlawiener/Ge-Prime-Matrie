import base64
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ge_prime.encode import encode_word
from gpm.compiler import compile_text
from gpm.format import read_gpm
from pipeline.size_compare import (
    compare_decode_word,
    compare_encode_batch,
    compare_encoded_word,
    compare_gpm_document,
    gpm_si_binary_bytes,
    json_bytes,
    substance_byte_len,
)
from pipeline.document_formats import (
    build_minimal_pdf,
    html_file_bytes,
    md_file_bytes,
    pdf_file_bytes,
    pdf_page_count,
    txt_file_bytes,
    utf8_len,
    zip_utf8_bytes,
)
from web.app import app


class TestSizeCompareCore(unittest.TestCase):
    def test_utf8_len(self):
        self.assertEqual(utf8_len(""), 0)
        self.assertEqual(utf8_len("A"), 1)
        self.assertEqual(utf8_len("ß"), 2)

    def test_json_bytes_compact(self):
        self.assertEqual(json_bytes({"s": 1, "i": 2}), len('{"s":1,"i":2}'))

    def test_substance_byte_len(self):
        self.assertEqual(substance_byte_len(0), 1)
        self.assertEqual(substance_byte_len(255), 1)
        self.assertEqual(substance_byte_len(256), 2)

    def test_gpm_si_binary_bytes(self):
        from gpm.int_codec import perm_width_bytes, width_bytes_for_class, substance_width_class

        s, i = encode_word("HALLO")
        expected = width_bytes_for_class(substance_width_class(s)) + perm_width_bytes("HALLO")
        self.assertEqual(gpm_si_binary_bytes(s, i, normalized="HALLO"), expected)

    def test_compare_encoded_word_exact_counts(self):
        original = "HALLO"
        normalized = "HALLO"
        substance, perm_index = encode_word(normalized)
        cmp = compare_encoded_word(
            original=original,
            normalized=normalized,
            substance=substance,
            perm_index=perm_index,
        )
        by_id = {r.id: r for r in cmp.rows}
        self.assertEqual(by_id["plain_original"].bytes, utf8_len(original))
        self.assertEqual(by_id["json_si_minimal"].bytes, json_bytes({"s": substance, "i": perm_index}))
        self.assertEqual(by_id["binary_si"].bytes, gpm_si_binary_bytes(substance, perm_index, normalized=normalized))
        self.assertLess(by_id["binary_si"].bytes, by_id["json_si_minimal"].bytes)
        self.assertEqual(len(cmp.calculation), 7)
        self.assertIn("headline", cmp.insight)
        self.assertIn(cmp.insight["verdict"], ("win", "tie", "learn"))

    def test_long_word_si_can_exceed_plain(self):
        word = "Wissenschaftlichkeit"
        substance, perm_index = encode_word(word)
        cmp = compare_encoded_word(
            original=word,
            normalized=word,
            substance=substance,
            perm_index=perm_index,
        )
        by_id = {r.id: r for r in cmp.rows}
        self.assertGreater(by_id["json_si_minimal"].bytes, by_id["plain_original"].bytes)
        # Kurzes Wort kann je nach S-Länge trotzdem „win“ sein — JSON > Klartext bleibt aussagekräftig
        self.assertGreater(by_id["json_si_minimal"].bytes, by_id["file_txt"].bytes)

    def test_compare_decode_word(self):
        substance, perm_index = encode_word("TEST")
        cmp = compare_decode_word(word="TEST", substance=substance, perm_index=perm_index)
        self.assertEqual(cmp.subject, "decode_word")
        self.assertEqual(cmp.calculation[0]["label"], "Rekonstruktion")

    def test_compare_gpm_document_file_bytes(self):
        text = "Hallo, Welt! Nochmal Hallo."
        _, blob, _ = compile_text(text)
        cmp = compare_gpm_document(source_text=text, blob=blob)
        by_id = {r.id: r for r in cmp.rows}
        self.assertEqual(by_id["gpm_file"].bytes, len(blob))
        self.assertEqual(by_id["source_utf8"].bytes, utf8_len(text))
        self.assertGreater(by_id["json_export"].bytes, by_id["gpm_file"].bytes)
        self.assertIn("file_pdf", by_id)
        self.assertIn("file_md", by_id)
        self.assertGreater(by_id["file_pdf"].bytes, txt_b := by_id["file_txt"].bytes)
        data = cmp.to_dict()
        self.assertIn("insight", data)
        self.assertGreaterEqual(len(data["insight"]["points"]), 2)
        stats = data["insight"]["stats"]
        self.assertEqual(stats["breakdown_sum"], len(blob))
        self.assertEqual(
            stats["file_header_bytes"]
            + stats["genome_bytes"]
            + stats["body_bytes"]
            + stats["separator_bytes"]
            + stats["explicit_bytes"]
            + stats["crc_bytes"],
            len(blob),
        )

    def test_gpm_file_breakdown_sums(self):
        from pipeline.size_compare import gpm_file_breakdown

        for text in ("Hallo Welt", "McDonald test", "Preis: 99€ super 🎉"):
            _, blob, stats = compile_text(text)
            doc = read_gpm(blob)
            bd = gpm_file_breakdown(doc, blob)
            self.assertEqual(bd["payload_sum"], len(blob), text)
            self.assertEqual(bd["genome_bytes"], stats.header_bytes, text)
            self.assertEqual(bd["body_bytes"], stats.body_bytes, text)
            self.assertEqual(bd["separator_bytes"], stats.separator_bytes, text)

    def test_compare_encode_batch(self):
        words = []
        for w in ("A", "B", "C"):
            s, i = encode_word(w)
            words.append({"original": w, "normalized": w, "substance": s, "perm_index": i})
        cmp = compare_encode_batch(words)
        by_id = {r.id: r for r in cmp.rows}
        joined = " ".join(w["original"] for w in words)
        self.assertEqual(by_id["batch_joined_utf8"].bytes, utf8_len(joined))
        self.assertEqual(by_id["batch_sum_plain"].bytes, 3)
        self.assertEqual(
            by_id["batch_sum_json_si"].bytes,
            sum(json_bytes({"s": w["substance"], "i": w["perm_index"]}) for w in words),
        )
        self.assertEqual(
            by_id["batch_sum_binary_si"].bytes,
            sum(
                gpm_si_binary_bytes(w["substance"], w["perm_index"], normalized=w["normalized"])
                for w in words
            ),
        )
        self.assertEqual(cmp.insight["baseline_bytes"], utf8_len(joined))

    def test_compare_encoded_word_all_row_bytes(self):
        original = "Straße"
        normalized = "STRAßE"
        substance, perm_index = encode_word(normalized)
        cmp = compare_encoded_word(
            original=original,
            normalized=normalized,
            substance=substance,
            perm_index=perm_index,
        )
        by_id = {r.id: r for r in cmp.rows}
        text_si_str = f"S={substance}\nI={perm_index}"
        expected = {
            "plain_original": utf8_len(original),
            "plain_normalized": utf8_len(normalized),
            "file_txt": txt_file_bytes(original),
            "file_md": md_file_bytes(original, title=original[:40] or "Wort"),
            "json_si_minimal": json_bytes({"s": substance, "i": perm_index}),
            "json_si_api": json_bytes(
                {"substance": substance, "perm_index": perm_index, "normalized": normalized}
            ),
            "text_si": utf8_len(text_si_str),
            "csv_line": utf8_len(f"{original},{substance},{perm_index}"),
            "hex_si": utf8_len(f"{substance:x},{perm_index}"),
            "base64_utf8": len(base64.b64encode(original.encode("utf-8"))),
            "binary_si": gpm_si_binary_bytes(substance, perm_index, normalized=normalized),
        }
        for row_id, size in expected.items():
            self.assertEqual(by_id[row_id].bytes, size, row_id)
        for step in cmp.calculation:
            if "bytes" not in step:
                continue
            label = step["label"]
            if label == "Klartext":
                self.assertEqual(step["bytes"], expected["plain_original"])
            elif label == "JSON minimal":
                self.assertEqual(step["bytes"], expected["json_si_minimal"])
            elif label == "Binär S(I) gesamt":
                self.assertEqual(step["bytes"], expected["binary_si"])

    def test_pdf_page_count_matches_minimal_pdf(self):
        for text in ("kurz", "a\n" * 48, "a\n" * 49, "zeile\n" * 100):
            blob = build_minimal_pdf(text)
            match = re.search(rb"/Count (\d+)", blob)
            self.assertIsNotNone(match, text)
            self.assertEqual(pdf_page_count(text), int(match.group(1)), text)


class TestSizeCompareApi(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True

    def test_api_encode_word(self):
        substance, perm_index = encode_word("HALLO")
        with app.test_client() as client:
            resp = client.post(
                "/api/size/encode-word",
                json={
                    "original": "HALLO",
                    "normalized": "HALLO",
                    "substance": substance,
                    "perm_index": perm_index,
                },
            )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["subject"], "encode_word")
        self.assertIn("insight", data)
        self.assertGreaterEqual(len(data["rows"]), 5)
        self.assertGreaterEqual(len(data["calculation"]), 7)

    def test_api_decode(self):
        substance, perm_index = encode_word("WELT")
        with app.test_client() as client:
            resp = client.post(
                "/api/size/decode",
                json={"substance": substance, "perm_index": perm_index},
            )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["subject"], "decode_word")

    def test_api_gpm(self):
        text = "Test GPM Größe."
        _, blob, _ = compile_text(text)
        with app.test_client() as client:
            resp = client.post(
                "/api/size/gpm",
                json={
                    "source_text": text,
                    "file_base64": base64.b64encode(blob).decode("ascii"),
                },
            )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["subject"], "gpm_document")
        gpm = next(r for r in data["rows"] if r["id"] == "gpm_file")
        self.assertEqual(gpm["bytes"], len(blob))
        stats = data["insight"]["stats"]
        self.assertEqual(stats["breakdown_sum"], len(blob))

    def test_api_invalid_si(self):
        with app.test_client() as client:
            resp = client.post("/api/size/decode", json={"substance": 0, "perm_index": 1})
        self.assertEqual(resp.status_code, 400)


class TestDocumentFormats(unittest.TestCase):
    def test_txt_md_html_sizes(self):
        text = "Größe\nZeile zwei"
        self.assertEqual(txt_file_bytes(text), utf8_len(text))
        self.assertGreater(md_file_bytes(text), txt_file_bytes(text))
        self.assertGreater(html_file_bytes(text), txt_file_bytes(text))

    def test_pdf_starts_with_header(self):
        blob = build_minimal_pdf("Hallo PDF")
        self.assertTrue(blob.startswith(b"%PDF-1.4"))
        self.assertEqual(pdf_file_bytes("Hallo PDF"), len(blob))

    def test_pdf_page_count_single_line(self):
        self.assertEqual(pdf_page_count("Hallo"), 1)
        self.assertEqual(pdf_page_count("a\n" * 48), 1)
        self.assertEqual(pdf_page_count("a\n" * 49), 2)

    def test_zip_smaller_than_plain_for_repetitive_text(self):
        text = "Wort " * 500
        self.assertLess(zip_utf8_bytes(text), utf8_len(text))
