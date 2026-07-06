"""Storage size comparison — language-neutral API (Invariant I2-F)."""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass, field
from typing import Any

from analysis.binary.int_codec import (
    perm_width_bytes,
    substance_width_class,
    width_bytes_for_class,
    width_class_for_magnitude,
)
from analysis.storage.document_formats import md_file_bytes, txt_file_bytes, utf8_len

CATEGORY_ORDER = ("document", "gpm", "structured", "transport")


@dataclass(frozen=True)
class WordSnapshot:
    original: str
    normalized: str
    substance: int
    perm_index: int


@dataclass(frozen=True)
class FormatSize:
    id: str
    bytes: int
    sample: str
    is_gpm: bool = False
    ext: str = ""
    category: str = "document"
    formula_id: str = ""


@dataclass
class SizeComparison:
    subject: str
    rows: list[FormatSize]
    calculation: list[dict[str, Any]]
    insight: dict[str, Any]
    highlight_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        max_bytes = max((r.bytes for r in self.rows), default=1)
        return {
            "subject": self.subject,
            "highlight_ids": self.highlight_ids,
            "insight": self.insight,
            "max_bytes": max_bytes,
            "calculation": self.calculation,
            "rows": [
                {
                    "id": r.id,
                    "bytes": r.bytes,
                    "sample": r.sample,
                    "is_gpm": r.is_gpm,
                    "ext": r.ext,
                    "category": r.category,
                    "formula_id": r.formula_id,
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
    one_line = " ".join(str(text).split())
    if len(one_line) <= limit:
        return one_line
    return one_line[: limit - 1] + "…"


def _calc(step_id: str, *, size: int | None = None, detail_params: dict[str, Any] | None = None) -> dict:
    step: dict[str, Any] = {"step_id": step_id}
    if size is not None:
        step["bytes"] = size
    if detail_params:
        step["detail_params"] = detail_params
    return step


def _sort_rows(rows: list[FormatSize]) -> list[FormatSize]:
    order = {cat: idx for idx, cat in enumerate(CATEGORY_ORDER)}
    return sorted(rows, key=lambda r: (r.bytes, order.get(r.category, 99), r.id))


def gpm_si_binary_bytes(substance: int, perm_index: int, *, normalized: str = "") -> int:
    s_bytes = width_bytes_for_class(substance_width_class(substance))
    if normalized:
        i_bytes = perm_width_bytes(normalized)
    else:
        i_bytes = width_bytes_for_class(width_class_for_magnitude(perm_index))
    return s_bytes + i_bytes


def _insight_for_word(*, best_plain: int, best_gpm: int) -> dict[str, Any]:
    saved = best_plain - best_gpm
    pct = round(100 * saved / best_plain) if best_plain else 0
    if best_gpm < best_plain:
        verdict = "win"
        points = [
            {"id": "baseline_vs_gpm", "params": {"plain": best_plain, "gpm": best_gpm}},
            {"id": "substance_grows", "params": {}},
            {"id": "gpm_dedup", "params": {}},
        ]
    elif best_gpm == best_plain:
        verdict = "tie"
        points = [
            {"id": "same_size", "params": {}},
            {"id": "exact_perm", "params": {}},
        ]
    else:
        verdict = "learn"
        points = [
            {"id": "short_word", "params": {"plain": best_plain, "gpm": best_gpm}},
            {"id": "substance_scales", "params": {}},
            {"id": "dedup_benefit", "params": {}},
        ]
    return {
        "verdict": verdict,
        "baseline_bytes": best_plain,
        "best_gpm_bytes": best_gpm,
        "saved_bytes": saved,
        "pct_saved": pct,
        "points": points,
    }


def compare_word_snapshot(snapshot: WordSnapshot) -> SizeComparison:
    original = snapshot.original
    normalized = snapshot.normalized
    substance = snapshot.substance
    perm_index = snapshot.perm_index

    s_text = str(substance)
    i_text = str(perm_index)

    plain_orig = utf8_len(original)
    plain_norm = utf8_len(normalized)
    txt_b = txt_file_bytes(original)
    md_b = md_file_bytes(original, title=original[:40] or "word")
    json_min = json_bytes({"s": substance, "i": perm_index})
    json_api = json_bytes({"substance": substance, "perm_index": perm_index, "normalized": normalized})
    text_si_str = f"S={substance}\nI={perm_index}"
    text_si = utf8_len(text_si_str)
    csv_line = utf8_len(f"{original},{substance},{perm_index}")
    b64_plain = len(base64.b64encode(original.encode("utf-8")))
    hex_line = utf8_len(f"{substance:x},{perm_index}")
    binary_si = gpm_si_binary_bytes(substance, perm_index, normalized=normalized)
    s_bin = width_bytes_for_class(substance_width_class(substance))
    i_bin = perm_width_bytes(normalized)

    rows = [
        FormatSize("file_txt", txt_b, _sample(original), ext=".txt", category="document"),
        FormatSize("file_md", md_b, "yaml_frontmatter", ext=".md", category="document"),
        FormatSize("plain_original", plain_orig, _sample(original), category="document"),
        FormatSize("plain_normalized", plain_norm, _sample(normalized), category="document"),
        FormatSize(
            "binary_si",
            binary_si,
            f"{s_bin}+{i_bin}",
            is_gpm=True,
            ext=".si",
            category="gpm",
            formula_id="genome_geometry",
        ),
        FormatSize(
            "json_si_minimal",
            json_min,
            _sample(json.dumps({"s": substance, "i": perm_index}, separators=(",", ":"))),
            is_gpm=True,
            ext=".json",
            category="gpm",
        ),
        FormatSize(
            "json_si_api",
            json_api,
            "substance_perm_normalized",
            is_gpm=True,
            ext=".json",
            category="gpm",
        ),
        FormatSize("csv_line", csv_line, "word_s_i", ext=".csv", category="structured"),
        FormatSize("text_si", text_si, _sample(text_si_str, 48), ext=".txt", category="structured"),
        FormatSize("hex_si", hex_line, _sample(hex_line, 48), category="structured"),
        FormatSize("base64_utf8", b64_plain, "api_overhead", ext=".b64", category="transport"),
    ]

    calculation = [
        _calc("plain", size=plain_orig, detail_params={"original": original, "chars": len(original)}),
        _calc("s_decimal", size=utf8_len(s_text), detail_params={"substance": substance, "digits": len(s_text)}),
        _calc("i_decimal", size=utf8_len(i_text), detail_params={"perm_index": perm_index}),
        _calc("storage_s_genome", size=s_bin, detail_params={"bytes": s_bin}),
        _calc(
            "storage_i_geometry",
            size=i_bin,
            detail_params={"bytes": i_bin, "normalized": normalized},
        ),
        _calc(
            "binary_si_total",
            size=binary_si,
            detail_params={"s_bytes": s_bin, "i_bytes": i_bin},
        ),
        _calc("json_minimal", size=json_min),
    ]

    best_plain = min(plain_orig, plain_norm, txt_b)
    best_gpm = min(json_min, binary_si)
    insight = _insight_for_word(best_plain=best_plain, best_gpm=best_gpm)

    return SizeComparison(
        subject="encode_word",
        rows=_sort_rows(rows),
        calculation=calculation,
        insight=insight,
        highlight_ids=["json_si_minimal", "binary_si"],
    )


def _insight_for_batch(*, best_plain: int, best_gpm: int, word_count: int) -> dict[str, Any]:
    saved = best_plain - best_gpm
    pct = round(100 * saved / best_plain) if best_plain else 0
    if best_gpm < best_plain:
        verdict = "win"
        points = [
            {"id": "baseline_vs_gpm", "params": {"plain": best_plain, "gpm": best_gpm}},
            {"id": "gpm_repeat_once", "params": {}},
        ]
    else:
        verdict = "learn"
        points = [
            {"id": "baseline_vs_gpm", "params": {"plain": best_plain, "gpm": best_gpm}},
            {"id": "short_words_gpm", "params": {"count": word_count}},
        ]
    return {
        "verdict": verdict,
        "baseline_bytes": best_plain,
        "best_gpm_bytes": best_gpm,
        "saved_bytes": saved,
        "pct_saved": pct,
        "points": points,
    }


def compare_batch_snapshots(snapshots: list[WordSnapshot]) -> SizeComparison:
    if not snapshots:
        raise ValueError("empty_word_list")

    originals = [s.original for s in snapshots]
    joined = " ".join(originals)
    joined_bytes = utf8_len(joined)
    txt_b = txt_file_bytes(joined)
    md_b = md_file_bytes(joined, title=f"{len(snapshots)}_words")

    sum_plain = sum(utf8_len(s.original) for s in snapshots)
    sum_json_si = sum(json_bytes({"s": s.substance, "i": s.perm_index}) for s in snapshots)
    sum_binary_si = sum(
        gpm_si_binary_bytes(s.substance, s.perm_index, normalized=s.normalized) for s in snapshots
    )
    csv_all_str = "\n".join(f"{s.original},{s.substance},{s.perm_index}" for s in snapshots)
    csv_all = utf8_len(csv_all_str)

    rows = [
        FormatSize(
            "batch_joined_utf8",
            joined_bytes,
            _sample(joined, 56),
            ext=".txt",
            category="document",
        ),
        FormatSize("batch_txt", txt_b, f"{len(snapshots)}_words", ext=".txt", category="document"),
        FormatSize("batch_md", md_b, "frontmatter_words", ext=".md", category="document"),
        FormatSize("batch_sum_plain", sum_plain, "no_spaces", category="document"),
        FormatSize(
            "batch_sum_json_si",
            sum_json_si,
            f"{len(snapshots)}_json_si",
            is_gpm=True,
            ext=".json",
            category="gpm",
        ),
        FormatSize(
            "batch_sum_binary_si",
            sum_binary_si,
            f"{len(snapshots)}_binary_si",
            is_gpm=True,
            category="gpm",
        ),
        FormatSize("batch_csv", csv_all, "one_row_per_word", ext=".csv", category="structured"),
    ]

    calculation = [
        _calc(
            "plain_joined",
            size=joined_bytes,
            detail_params={"count": len(snapshots), "joined": _sample(joined, 40)},
        ),
        _calc(
            "sum_json_si",
            size=sum_json_si,
            detail_params={"avg": sum_json_si // len(snapshots), "count": len(snapshots)},
        ),
        _calc("sum_binary_si", size=sum_binary_si, detail_params={"count": len(snapshots)}),
        _calc("sum_plain_words", size=sum_plain, detail_params={"count": len(snapshots)}),
    ]

    best_plain = joined_bytes
    best_gpm = min(sum_json_si, sum_binary_si)
    insight = _insight_for_batch(best_plain=best_plain, best_gpm=best_gpm, word_count=len(snapshots))

    return SizeComparison(
        subject="encode_batch",
        rows=_sort_rows(rows),
        calculation=calculation,
        insight=insight,
        highlight_ids=["batch_sum_json_si", "batch_sum_binary_si"],
    )


def snapshot_from_document(*, original: str, normalized: str, substance: int, perm_index: int) -> WordSnapshot:
    return WordSnapshot(
        original=original,
        normalized=normalized,
        substance=substance,
        perm_index=perm_index,
    )


def compare_decode_snapshot(snapshot: WordSnapshot) -> SizeComparison:
    cmp = compare_word_snapshot(snapshot)
    word_bytes = utf8_len(snapshot.original)
    reconstruction = _calc(
        "reconstruction",
        size=word_bytes,
        detail_params={"word": snapshot.original},
    )
    points = [
        {"id": "decoded_word", "params": {"word": snapshot.original, "bytes": word_bytes}},
        *cmp.insight.get("points", []),
    ]
    return SizeComparison(
        subject="decode_word",
        rows=cmp.rows,
        calculation=[reconstruction, *cmp.calculation],
        insight={
            **cmp.insight,
            "points": points,
        },
        highlight_ids=cmp.highlight_ids,
    )
