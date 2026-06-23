"""
Speichervergleich: GPM S(I) / .gpm vs. gängige Text- und Datenformate.

Exakte Byte-Zählung (UTF-8, echte PDF/ZIP-Strukturen) mit strukturierten Insights.
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass, field

from gpm.format import read_file_header_fields, read_gpm
from gpm.model import GpmDocument
from pipeline.document_formats import (
    html_file_bytes,
    human_bytes,
    md_file_bytes,
    pdf_file_bytes,
    pdf_page_count,
    txt_file_bytes,
    utf8_len,
    zip_utf8_bytes,
)

CATEGORY_ORDER = ("document", "gpm", "structured", "transport")
CATEGORY_LABELS = {
    "document": "Dokumente",
    "gpm": "GPM / Geometrie",
    "structured": "Strukturiert (Daten)",
    "transport": "Transport & Archive",
}


@dataclass(frozen=True)
class FormatSize:
    id: str
    label: str
    bytes: int
    sample: str
    note: str = ""
    is_gpm: bool = False
    ext: str = ""
    category: str = "document"
    formula: str = ""


@dataclass
class SizeComparison:
    subject: str
    rows: list[FormatSize]
    calculation: list[dict]
    insight: dict
    highlight_ids: list[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> dict:
        max_bytes = max((r.bytes for r in self.rows), default=1)
        return {
            "subject": self.subject,
            "highlight_ids": self.highlight_ids,
            "summary": self.summary or self.insight.get("lede", ""),
            "insight": self.insight,
            "max_bytes": max_bytes,
            "categories": CATEGORY_LABELS,
            "calculation": self.calculation,
            "rows": [
                {
                    "id": r.id,
                    "label": r.label,
                    "bytes": r.bytes,
                    "human": human_bytes(r.bytes),
                    "sample": r.sample,
                    "note": r.note,
                    "is_gpm": r.is_gpm,
                    "ext": r.ext,
                    "category": r.category,
                    "formula": r.formula,
                    "pct_of_max": round(100 * r.bytes / max_bytes, 1) if max_bytes else 0,
                }
                for r in self.rows
            ],
        }


def json_bytes(obj: object, *, pretty: bool = False) -> int:
    if pretty:
        raw = json.dumps(obj, ensure_ascii=False, indent=2)
    else:
        raw = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    return utf8_len(raw)


def _sample(text: str, limit: int = 72) -> str:
    text = str(text)
    one_line = " ".join(text.split())
    if len(one_line) <= limit:
        return one_line
    return one_line[: limit - 1] + "…"


def _calc(label: str, detail: str, *, size: int | None = None) -> dict:
    step = {"label": label, "detail": detail}
    if size is not None:
        step["bytes"] = size
        step["human"] = human_bytes(size)
    return step


def _sort_rows(rows: list[FormatSize]) -> list[FormatSize]:
    order = {cat: idx for idx, cat in enumerate(CATEGORY_ORDER)}
    return sorted(rows, key=lambda r: (r.bytes, order.get(r.category, 99), r.label))


def substance_byte_len(substance: int) -> int:
    if substance < 0:
        raise ValueError("Substanz darf nicht negativ sein.")
    if substance == 0:
        return 1
    return (substance.bit_length() + 7) // 8


def _explicit_payload_bytes(document: GpmDocument) -> int:
    """Größe des Explicit-Overflow-Segments (wie in gpm/format.py)."""
    total = 0
    for _token_index, text in document.explicit:
        total += 8 + utf8_len(text)
    return total


def gpm_file_breakdown(document: GpmDocument, blob: bytes) -> dict:
    """Exakte Byte-Aufteilung einer .gpm-Datei (Summe = len(blob))."""
    from gpm.format import (
        FILE_HEADER_SIZE,
        LEGACY_VERSION,
        VERSION,
        VERSION_V2,
        VERSION_V3,
        VERSION_V4,
    )
    from gpm import body_payload_bytes, genome_payload_bytes

    version = blob[3] if len(blob) >= 4 and blob[:3] == b"GPM" else 0
    gpm_ver, separator_perm, separator_bytes = read_file_header_fields(blob)
    if gpm_ver == VERSION_V2:
        separator_bytes = sum(4 + utf8_len(g) for g in document.gaps)

    genome_bytes = genome_payload_bytes(document, version=version)
    body_bytes = body_payload_bytes(document, version=version, data=blob)
    explicit_bytes = _explicit_payload_bytes(document)
    crc_bytes = 4
    file_header_bytes = (
        FILE_HEADER_SIZE
        if version in (VERSION, VERSION_V4, VERSION_V3, VERSION_V2)
        else 18
        if version == LEGACY_VERSION
        else FILE_HEADER_SIZE
    )
    payload_total = (
        file_header_bytes
        + genome_bytes
        + body_bytes
        + separator_bytes
        + explicit_bytes
        + crc_bytes
    )
    return {
        "version": version,
        "file_bytes": len(blob),
        "file_header_bytes": file_header_bytes,
        "genome_bytes": genome_bytes,
        "body_bytes": body_bytes,
        "separator_bytes": separator_bytes,
        "separator_perm": separator_perm,
        "explicit_bytes": explicit_bytes,
        "explicit_count": len(document.explicit),
        "crc_bytes": crc_bytes,
        "unique_words": len(document.header),
        "tokens": len(document.tokens),
        "payload_sum": payload_total,
    }


def gpm_si_binary_bytes(substance: int, perm_index: int, *, normalized: str = "") -> int:
    """Tiered S(I) wie .gpm v4: S-Stufe + I-Stufe aus Permutationsraum."""
    from gpm.int_codec import (
        perm_width_bytes,
        width_bytes_for_class,
        width_class_for_magnitude,
        substance_width_class,
    )

    s_bytes = width_bytes_for_class(substance_width_class(substance))
    if normalized:
        i_bytes = perm_width_bytes(normalized)
    else:
        i_bytes = width_bytes_for_class(width_class_for_magnitude(perm_index))
    return s_bytes + i_bytes


def gpm_si_tier_label(substance: int, perm_index: int, *, normalized: str = "") -> str:
    """Lesbare Stufen-Beschreibung für UI/Rechenschritte."""
    from gpm.int_codec import (
        perm_width_bytes,
        width_bytes_for_class,
        width_class_for_magnitude,
        substance_width_class,
    )

    s_bytes = width_bytes_for_class(substance_width_class(substance))
    if normalized:
        i_bytes = perm_width_bytes(normalized)
    else:
        i_bytes = width_bytes_for_class(width_class_for_magnitude(perm_index))
    return f"Genom S {s_bytes} B + Geometrie I {i_bytes} B = {s_bytes + i_bytes} B"


def compare_encoded_word(
    *,
    original: str,
    normalized: str,
    substance: int,
    perm_index: int,
) -> SizeComparison:
    s_text = str(substance)
    i_text = str(perm_index)

    plain_orig = utf8_len(original)
    plain_norm = utf8_len(normalized)
    txt_b = txt_file_bytes(original)
    md_b = md_file_bytes(original, title=original[:40] or "Wort")
    json_min = json_bytes({"s": substance, "i": perm_index})
    json_api = json_bytes(
        {"substance": substance, "perm_index": perm_index, "normalized": normalized}
    )
    text_si_str = f"S={substance}\nI={perm_index}"
    text_si = utf8_len(text_si_str)
    csv_line = utf8_len(f"{original},{substance},{perm_index}")
    b64_plain = len(base64.b64encode(original.encode("utf-8")))
    hex_line = utf8_len(f"{substance:x},{perm_index}")
    binary_si = gpm_si_binary_bytes(substance, perm_index, normalized=normalized)
    tier_label = gpm_si_tier_label(substance, perm_index, normalized=normalized)
    from gpm.int_codec import perm_width_bytes, width_bytes_for_class, substance_width_class

    s_bin = width_bytes_for_class(substance_width_class(substance))
    i_bin = perm_width_bytes(normalized)

    rows = [
        FormatSize("file_txt", "Textdatei", txt_b, _sample(original), ext=".txt", category="document", formula="UTF-8"),
        FormatSize("file_md", "Markdown", md_b, "YAML-Frontmatter + Text", ext=".md", category="document"),
        FormatSize("plain_original", "Klartext (Original)", plain_orig, _sample(original), category="document"),
        FormatSize("plain_normalized", "Klartext (normalisiert)", plain_norm, _sample(normalized), category="document"),
        FormatSize(
            "binary_si",
            "Binär S(I)",
            binary_si,
            f"{s_bin} B S (Genom) + {i_bin} B I (Geometrie)",
            is_gpm=True,
            ext=".si",
            category="gpm",
            formula=f"Substanz {s_bin} B im Genom + Index {i_bin} B in der Geometrie",
        ),
        FormatSize(
            "json_si_minimal",
            "JSON S(I) minimal",
            json_min,
            _sample(json.dumps({"s": substance, "i": perm_index}, separators=(",", ":"))),
            is_gpm=True,
            ext=".json",
            category="gpm",
        ),
        FormatSize(
            "json_si_api",
            "JSON S(I) API",
            json_api,
            "substance, perm_index, normalized",
            is_gpm=True,
            ext=".json",
            category="gpm",
        ),
        FormatSize("csv_line", "CSV-Zeile", csv_line, "Wort,S,I", ext=".csv", category="structured"),
        FormatSize("text_si", "Text S=/I=", text_si, _sample(text_si_str, 48), ext=".txt", category="structured"),
        FormatSize("hex_si", "Hex S + I", hex_line, _sample(hex_line, 48), category="structured"),
        FormatSize(
            "base64_utf8",
            "Base64 (Klartext)",
            b64_plain,
            "+33 % typisch in APIs",
            ext=".b64",
            category="transport",
        ),
    ]

    calculation = [
        _calc("Klartext", f"„{original}“ → {plain_orig} B ({len(original)} Zeichen UTF-8)", size=plain_orig),
        _calc("S (Dezimal)", f"{substance} → {utf8_len(s_text)} B ({len(s_text)} Ziffern)", size=utf8_len(s_text)),
        _calc("I (Dezimal)", f"{perm_index} → {utf8_len(i_text)} B", size=utf8_len(i_text)),
        _calc("Speicher S (Genom)", f"Substanz als {s_bin}-Byte-Ganzzahl", size=s_bin),
        _calc("Speicher I (Geometrie)", f"Index als {i_bin}-Byte-Ganzzahl (N aus „{normalized}“)", size=i_bin),
        _calc("Binär S(I) gesamt", tier_label, size=binary_si),
        _calc("JSON minimal", '{"s":…,"i":…}', size=json_min),
    ]

    best_plain = min(plain_orig, plain_norm, txt_b)
    best_gpm = min(json_min, binary_si)
    highlight_ids = ["json_si_minimal", "binary_si"]

    if best_gpm < best_plain:
        verdict = "win"
        saved = best_plain - best_gpm
        pct = round(100 * saved / best_plain) if best_plain else 0
        headline = f"S(I) spart {human_bytes(saved)} ({pct} %)"
        points = [
            f"Klartext: {human_bytes(best_plain)} · kleinstes S(I): {human_bytes(best_gpm)}",
            f"S hat {len(s_text)} Dezimalstellen, bei langen Wörtern wächst der Vorteil",
            "In .gpm zählen Wiederholungen nur einmal im Genom",
        ]
    elif best_gpm == best_plain:
        verdict = "tie"
        headline = "Gleich groß wie Klartext"
        points = ["S(I) und Textdatei liegen bei gleicher Byte-Zahl", "Vorteil: exakte Permutation + ggT-/kgV-Suche"]
    else:
        verdict = "learn"
        extra = best_gpm - best_plain
        headline = f"Klartext ist {human_bytes(extra)} kleiner"
        points = [
            f"Normal bei kurzen Wörtern ({human_bytes(best_plain)} Text vs. {human_bytes(best_gpm)} S/I)",
            "S(I) skaliert mit Substanz-Länge, nicht mit Buchstabenanzahl",
            "Nutzen: dedupliziertes Genom, Substanz-Matching",
        ]

    insight = {
        "headline": headline,
        "verdict": verdict,
        "lede": points[0],
        "points": points,
        "baseline_label": "Klartext",
        "baseline_bytes": best_plain,
        "baseline_human": human_bytes(best_plain),
    }

    rows = _sort_rows(rows)
    return SizeComparison(
        subject="encode_word",
        rows=rows,
        calculation=calculation,
        insight=insight,
        summary=insight["lede"],
        highlight_ids=highlight_ids,
    )


def compare_decode_word(*, word: str, substance: int, perm_index: int) -> SizeComparison:
    cmp = compare_encoded_word(
        original=word,
        normalized=word,
        substance=substance,
        perm_index=perm_index,
    )
    cmp.subject = "decode_word"
    cmp.calculation.insert(
        0,
        _calc("Rekonstruktion", f"Wort „{word}“", size=utf8_len(word)),
    )
    cmp.insight = {
        **cmp.insight,
        "headline": "Decodiertes Wort vs. gespeichertes S(I)",
        "points": [f"Ergebnis: „{word}“ ({human_bytes(utf8_len(word))})"] + cmp.insight["points"],
    }
    cmp.summary = cmp.insight["lede"]
    return cmp


def _gpm_json_export_bytes(document: GpmDocument) -> int:
    payload = {
        "header": [
            {
                "word_id": e.word_id,
                "original": e.word_original,
                "normalized": e.word_normalized,
                "substance": e.substance,
            }
            for e in document.header
        ],
        "tokens": [
            {
                "word_id": t.word_id,
                "perm_index": t.perm_index,
                "case_code": t.case_code,
            }
            for t in document.tokens
        ],
        "gaps": document.gaps,
    }
    return json_bytes(payload)


def _words_only_bytes(document: GpmDocument) -> int:
    from gpm.reader import reconstruct_text

    text = reconstruct_text(document)
    words_only = " ".join(part for part in text.split() if part.strip())
    return utf8_len(words_only)


def compare_gpm_document(*, source_text: str, blob: bytes) -> SizeComparison:
    from gpm.separator_codec import perm_code_label

    document = read_gpm(blob)
    breakdown = gpm_file_breakdown(document, blob)
    source_bytes = utf8_len(source_text)
    file_bytes = len(blob)
    gpm_ver = breakdown["version"]
    separator_perm = breakdown["separator_perm"]
    separator_bytes = breakdown["separator_bytes"]
    genome_bytes = breakdown["genome_bytes"]
    body_bytes = breakdown["body_bytes"]
    explicit_bytes = breakdown["explicit_bytes"]
    file_header_bytes = breakdown["file_header_bytes"]
    crc_bytes = breakdown["crc_bytes"]
    txt_b = txt_file_bytes(source_text)
    md_b = md_file_bytes(source_text)
    html_b = html_file_bytes(source_text)
    pdf_b = pdf_file_bytes(source_text)
    zip_b = zip_utf8_bytes(source_text)
    json_export = _gpm_json_export_bytes(document)
    json_pretty = json_bytes(
        {
            "header": [
                {
                    "word_id": e.word_id,
                    "original": e.word_original,
                    "normalized": e.word_normalized,
                    "substance": e.substance,
                }
                for e in document.header
            ],
            "tokens": [
                {
                    "word_id": t.word_id,
                    "perm_index": t.perm_index,
                    "case_code": t.case_code,
                }
                for t in document.tokens
            ],
            "gaps": document.gaps,
        },
        pretty=True,
    )
    b64_source = len(base64.b64encode(source_text.encode("utf-8")))
    b64_gpm = len(base64.b64encode(blob))
    words_only = _words_only_bytes(document)
    page_est = pdf_page_count(source_text)

    rows = [
        FormatSize(
            "file_txt",
            "Textdatei",
            txt_b,
            "Reiner UTF-8-Inhalt",
            ext=".txt",
            category="document",
            formula=f"{len(source_text)} Zeichen UTF-8",
        ),
        FormatSize(
            "file_md",
            "Markdown",
            md_b,
            "Frontmatter + Quelltext",
            ext=".md",
            category="document",
        ),
        FormatSize(
            "file_html",
            "HTML (minimal)",
            html_b,
            "<pre> mit escaped Text",
            ext=".html",
            category="document",
        ),
        FormatSize(
            "words_spaced",
            "Nur Wörter + Leerzeichen",
            words_only,
            "Ohne Satzzeichen, nicht verlustfrei",
            ext=".txt",
            category="document",
        ),
        FormatSize(
            "file_zip",
            "ZIP (DEFLATE)",
            zip_b,
            "quelle.txt komprimiert",
            ext=".zip",
            category="transport",
            formula="ZIP-Store + zlib",
        ),
        FormatSize(
            "gpm_file",
            "Ge-Prime-Matrix .gpm",
            file_bytes,
            f"v{gpm_ver} · {breakdown['unique_words']} Wörter · {breakdown['tokens']} Token",
            is_gpm=True,
            ext=".gpm",
            category="gpm",
            formula=(
                f"Header {file_header_bytes} + Genom {genome_bytes} + Geometrie {body_bytes} + "
                f"Separator {separator_bytes} + Explicit {explicit_bytes} + CRC {crc_bytes}"
            ),
        ),
        FormatSize(
            "file_pdf",
            "PDF (minimal)",
            pdf_b,
            f"Helvetica · ~{page_est} Seite(n) · Flate",
            ext=".pdf",
            category="document",
            formula=f"PDF-Rahmen + {page_est}× Flate-Stream",
        ),
        FormatSize(
            "json_export",
            "JSON (minimal)",
            json_export,
            "Genom + Token + Separator",
            ext=".json",
            category="structured",
        ),
        FormatSize(
            "json_export_pretty",
            "JSON (formatiert)",
            json_pretty,
            "Wie Debug/API-Export",
            ext=".json",
            category="structured",
        ),
        FormatSize(
            "base64_source",
            "Base64 (Quelltext)",
            b64_source,
            "E-Mail / JSON-Anhang",
            category="transport",
        ),
        FormatSize(
            "base64_gpm",
            "Base64 (.gpm)",
            b64_gpm,
            "API-Transport",
            category="transport",
        ),
        FormatSize(
            "source_utf8",
            "Rohtext (Referenz)",
            source_bytes,
            _sample(source_text, 48),
            category="document",
            formula="Basis für alle Formate",
        ),
    ]

    ratio = file_bytes / source_bytes if source_bytes else 0
    json_factor = round(json_export / file_bytes, 1) if file_bytes else 0

    perm_label = perm_code_label(separator_perm) if gpm_ver >= 3 else "Legacy"
    calculation = [
        _calc("Quelltext", f"{len(source_text)} Zeichen UTF-8", size=source_bytes),
        _calc("Textdatei .txt", "identisch zum UTF-8-Inhalt", size=txt_b),
        _calc("Markdown .md", "Frontmatter + Text", size=md_b),
        _calc("HTML .html", "<!DOCTYPE> + <pre>", size=html_b),
        _calc("PDF .pdf", f"Minimal-PDF, {page_est} Seite(n), Flate", size=pdf_b),
        _calc("ZIP .zip", "quelle.txt, DEFLATE", size=zip_b),
        _calc(
            "Datei-Header",
            f"Magic GPM + Metadaten (v{gpm_ver})",
            size=file_header_bytes,
        ),
        _calc(
            "Genom",
            f"{breakdown['unique_words']} Wörter · S je 2/4/8/16 Byte im Genom",
            size=genome_bytes,
        ),
        _calc(
            "Geometrie",
            f"{breakdown['tokens']} Token · I je 2/4/8/16 Byte (Breite aus N)",
            size=body_bytes,
        ),
        _calc(
            "Separator",
            f"Perm {separator_perm} ({perm_label})",
            size=separator_bytes,
        ),
        _calc(
            "Explicit-Overflow",
            f"{breakdown['explicit_count']} Mischschreibweise(n)",
            size=explicit_bytes,
        ),
        _calc("CRC32", "Integritäts-Trailer", size=crc_bytes),
        _calc(
            ".gpm gesamt",
            f"{file_header_bytes}+{genome_bytes}+{body_bytes}+{separator_bytes}"
            f"+{explicit_bytes}+{crc_bytes} = {file_bytes} B",
            size=file_bytes,
        ),
        _calc("JSON-Export", "alle Strukturen serialisiert", size=json_export),
    ]

    highlight_ids = ["gpm_file"]

    if file_bytes < source_bytes:
        verdict = "win"
        saved = source_bytes - file_bytes
        pct = round(100 * saved / source_bytes)
        headline = f".gpm ist {pct} % kleiner als Klartext"
        points = [
            f"{human_bytes(source_bytes)} Text → {human_bytes(file_bytes)} .gpm",
            f"PDF wäre {human_bytes(pdf_b)} · ZIP {human_bytes(zip_b)}",
            f"JSON-Export {human_bytes(json_export)} ({json_factor}× größer als .gpm)",
            "Wörter im Genom nur einmal, ideal bei Wiederholungen",
        ]
    elif ratio <= 1.15:
        verdict = "tie"
        headline = ".gpm ≈ gleich groß wie Klartext"
        points = [
            f"Text {human_bytes(source_bytes)} · .gpm {human_bytes(file_bytes)}",
            f"Zusätzlich: verlustfreie Rekonstruktion, S(I)-Suche",
            f"JSON wäre {human_bytes(json_export)}",
        ]
    else:
        verdict = "learn"
        pct_over = round(100 * ratio - 100)
        headline = f".gpm ist {pct_over} % größer als reiner Text"
        points = [
            f"Quelltext {human_bytes(source_bytes)} · .gpm {human_bytes(file_bytes)} · PDF {human_bytes(pdf_b)}",
            f"Aufteilung: Header {file_header_bytes} · Genom {genome_bytes} · Geometrie {body_bytes} · "
            f"Separator {separator_bytes} · Explicit {explicit_bytes} · CRC {crc_bytes}",
            f"JSON-Export {human_bytes(json_export)}, {json_factor}× größer als .gpm",
            "Lohnt bei Wiederholungen, Substanz-Matching und exakter Rekonstruktion",
        ]

    insight = {
        "headline": headline,
        "verdict": verdict,
        "lede": points[0],
        "points": points,
        "baseline_label": "Quelltext (UTF-8)",
        "baseline_bytes": source_bytes,
        "baseline_human": human_bytes(source_bytes),
        "gpm_bytes": file_bytes,
        "gpm_human": human_bytes(file_bytes),
        "stats": {
            "unique_words": breakdown["unique_words"],
            "tokens": breakdown["tokens"],
            "separator_perm": separator_perm,
            "separator_bytes": separator_bytes,
            "file_header_bytes": file_header_bytes,
            "genome_bytes": genome_bytes,
            "body_bytes": body_bytes,
            "explicit_bytes": explicit_bytes,
            "crc_bytes": crc_bytes,
            "pdf_pages": page_est,
            "breakdown_sum": breakdown["payload_sum"],
        },
    }

    rows = _sort_rows(rows)
    return SizeComparison(
        subject="gpm_document",
        rows=rows,
        calculation=calculation,
        insight=insight,
        summary=insight["lede"],
        highlight_ids=highlight_ids,
    )


def compare_encode_batch(words: list[dict]) -> SizeComparison:
    if not words:
        raise ValueError("Keine Wörter zum Vergleichen.")

    originals = [w["original"] for w in words]
    joined = " ".join(originals)
    joined_bytes = utf8_len(joined)
    txt_b = txt_file_bytes(joined)
    md_b = md_file_bytes(joined, title=f"{len(words)} Wörter")

    sum_plain = sum(utf8_len(w["original"]) for w in words)
    sum_json_si = sum(json_bytes({"s": w["substance"], "i": w["perm_index"]}) for w in words)
    sum_binary_si = sum(
        gpm_si_binary_bytes(w["substance"], w["perm_index"], normalized=w.get("normalized", w["original"]))
        for w in words
    )
    csv_all_str = "\n".join(f"{w['original']},{w['substance']},{w['perm_index']}" for w in words)
    csv_all = utf8_len(csv_all_str)

    rows = [
        FormatSize("batch_joined_utf8", "Klartext (mit Leerzeichen)", joined_bytes, _sample(joined, 56), ext=".txt", category="document"),
        FormatSize("batch_txt", "Textdatei", txt_b, f"{len(words)} Wörter", ext=".txt", category="document"),
        FormatSize("batch_md", "Markdown", md_b, "Frontmatter + Wörter", ext=".md", category="document"),
        FormatSize("batch_sum_plain", "Summe Einzelwörter", sum_plain, "Ohne Leerzeichen dazwischen", category="document"),
        FormatSize(
            "batch_sum_json_si",
            "Summe JSON S(I)",
            sum_json_si,
            f"{len(words)} × {{\"s\",\"i\"}}",
            is_gpm=True,
            ext=".json",
            category="gpm",
        ),
        FormatSize(
            "batch_sum_binary_si",
            "Summe Binär S(I)",
            sum_binary_si,
            f"{len(words)} × (S + I tiered)",
            is_gpm=True,
            category="gpm",
        ),
        FormatSize("batch_csv", "CSV", csv_all, "Eine Zeile pro Wort", ext=".csv", category="structured"),
    ]

    calculation = [
        _calc(
            "Klartext",
            f'{len(words)} Wörter mit Leerzeichen („{ _sample(joined, 40)}“)',
            size=joined_bytes,
        ),
        _calc("Summe JSON S(I)", f"Ø {sum_json_si // len(words)} B/Wort", size=sum_json_si),
        _calc("Summe Binär S(I)", "Genom S + Geometrie I je Wort (2/4/8/16 Byte)", size=sum_binary_si),
        _calc(
            "Summe Einzelwörter",
            "ohne Leerzeichen, nur zum Vergleich, nicht als Datei",
            size=sum_plain,
        ),
    ]

    best_plain = joined_bytes  # realistischer Klartext inkl. Leerzeichen zwischen Wörtern
    best_gpm = min(sum_json_si, sum_binary_si)
    highlight_ids = ["batch_sum_json_si", "batch_sum_binary_si"]

    if best_gpm < best_plain:
        verdict = "win"
        headline = f"S(I)-Liste spart {human_bytes(best_plain - best_gpm)}"
        points = [
            f"Klartext {human_bytes(best_plain)} · S(I) gesamt {human_bytes(best_gpm)}",
            "In .gpm würden Wiederholungen nur einmal im Genom stehen",
        ]
    else:
        verdict = "learn"
        headline = "Klartext schlägt die S(I)-Summe"
        points = [
            f"Klartext {human_bytes(best_plain)} · S(I) gesamt {human_bytes(best_gpm)}",
            "Typisch bei kurzen Wörtern.gpm lohnt bei Dokumenten mit Wiederholungen",
        ]

    insight = {
        "headline": headline,
        "verdict": verdict,
        "lede": points[0],
        "points": points,
        "baseline_label": "Klartext",
        "baseline_bytes": best_plain,
        "baseline_human": human_bytes(best_plain),
    }

    rows = _sort_rows(rows)
    return SizeComparison(
        subject="encode_batch",
        rows=rows,
        calculation=calculation,
        insight=insight,
        summary=insight["lede"],
        highlight_ids=highlight_ids,
    )
