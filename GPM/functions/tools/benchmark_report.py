"""JSON- und Markdown-Reports für Profil-Benchmarks."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = ROOT / "docs" / "benchmark"


def _json_default(obj: Any) -> Any:
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Nicht serialisierbar: {type(obj)!r}")


def write_json_report(data: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=_json_default),
        encoding="utf-8",
    )


def derive_profile_limits(sweep_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregiert Grenzwerte pro Profil aus Sweep-Zeilen."""
    by_profile: dict[str, list[dict[str, Any]]] = {}
    for row in sweep_rows:
        by_profile.setdefault(row["profile"], []).append(row)

    limits: dict[str, Any] = {}
    for profile, rows in sorted(by_profile.items()):
        roundtrip_ok = [r for r in rows if r.get("roundtrip_ok")]
        unique_rows = [r for r in rows if r.get("pattern") == "unique" and r.get("roundtrip_ok")]
        all_same_ok = [r for r in rows if r.get("pattern") == "all_same" and r.get("roundtrip_ok")]
        lut_ok = [r for r in rows if r.get("lut_build_ok")]
        fits_16 = [r for r in rows if r.get("perm_fits_16")]

        max_l_roundtrip = max((r["length"] for r in unique_rows), default=0)
        max_l_lut = max((r["length"] for r in lut_ok if r["length"] <= 12), default=0)
        max_n_perm_fits_16 = max((r["N_perm"] for r in fits_16), default=0)
        max_dup = max((r["length"] for r in all_same_ok), default=0)

        first_fail = None
        for r in sorted(rows, key=lambda x: (x["length"], x["pattern"])):
            if r.get("failed_at"):
                first_fail = {
                    "length": r["length"],
                    "pattern": r["pattern"],
                    "failed_at": r["failed_at"],
                }
                break

        limits[profile] = {
            "alphabet_size": rows[0].get("alphabet_size", 0),
            "max_L_roundtrip_unique": max_l_roundtrip,
            "max_L_with_lut": max_l_lut,
            "max_N_perm_fits_16": max_n_perm_fits_16,
            "max_duplicate_count_all_same": max_dup,
            "roundtrip_at_L64_unique": any(
                r["length"] == 64 and r.get("pattern") == "unique" and r.get("roundtrip_ok")
                for r in rows
            ),
            "first_fail": first_fail,
            "complexity_class": _estimate_complexity(rows),
        }
    return limits


def _estimate_complexity(rows: list[dict[str, Any]]) -> str:
    """Heuristik aus encode_ms vs. L für erfolgreiche Roundtrips."""
    samples = [
        (r["length"], r.get("encode_si_ms") or 0)
        for r in rows
        if r.get("roundtrip_ok") and r.get("encode_si_ms") is not None
    ]
    if len(samples) < 2:
        return "unknown"
    samples.sort()
    l1, t1 = samples[0]
    l2, t2 = samples[-1]
    if l2 <= l1 or t2 <= 0:
        return "O(1)"
    ratio = (t2 / t1) / (l2 / l1) if t1 > 0 else 1.0
    if ratio < 1.5:
        return "O(L)"
    if ratio < 3.0:
        return "O(L log L)"
    return "O(N_perm)"


def _fmt_ms(value: float | None) -> str:
    if value is None:
        return "—"
    if value < 1:
        return f"{value:.3f}"
    if value < 100:
        return f"{value:.2f}"
    return f"{value:.1f}"


def write_markdown_report(
    meta: dict[str, Any],
    limits: dict[str, Any],
    sweep_rows: list[dict[str, Any]],
    path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "# Profil-Performance-Grenzen (Benchmark)",
        "",
        f"Generiert: {meta.get('generated_at', '—')}",
        f"Sweep-Punkte: {meta.get('total_sweep_points', 0)}",
        f"Width-Skips: {meta.get('width_skips', 0)}",
        "",
        "## Summary",
        "",
        "| Profil | Alphabet | max L (unique RT) | max dup (all_same) | max N_perm (16B) | LUT bis L | RT @ L=64 unique | Komplexität |",
        "|--------|----------|-------------------|--------------------|--------------------|-----------|------------------|-------------|",
    ]
    for profile, lim in sorted(limits.items()):
        lines.append(
            f"| {profile} | {lim['alphabet_size']} | {lim['max_L_roundtrip_unique']} "
            f"| {lim['max_duplicate_count_all_same']} | {lim['max_N_perm_fits_16']} "
            f"| {lim['max_L_with_lut']} | {'ja' if lim['roundtrip_at_L64_unique'] else 'nein'} "
            f"| {lim['complexity_class']} |"
        )

    lines.extend(["", "## Duplikat-Matrix (Auszug)", ""])
    dup_rows = [r for r in sweep_rows if r.get("section") == "duplicate_matrix"]
    if dup_rows:
        lines.append("| Profil | L | k (all_same) | N_perm | perm_fits_16 | roundtrip | failed_at |")
        lines.append("|--------|---|--------------|--------|--------------|-----------|-----------|")
        for r in dup_rows:
            lines.append(
                f"| {r['profile']} | {r['length']} | {r.get('multiplicity_k', '—')} "
                f"| {r.get('N_perm', '—')} | {r.get('perm_fits_16')} "
                f"| {r.get('roundtrip_ok')} | {r.get('failed_at') or '—'} |"
            )
    else:
        lines.append("_Keine Duplikat-Matrix-Daten._")

    lines.extend(["", "## Timing @ L=32 unique (ms)", ""])
    lines.append("| Profil | normalize | substance | perm_index | encode | decode | roundtrip |")
    lines.append("|--------|-----------|-----------|------------|--------|--------|-----------|")
    for profile in sorted(limits.keys()):
        row = next(
            (
                r
                for r in sweep_rows
                if r.get("profile") == profile
                and r.get("length") == 32
                and r.get("pattern") == "unique"
                and r.get("section") == "main"
            ),
            None,
        )
        if row is None:
            lines.append(f"| {profile} | — | — | — | — | — | — |")
            continue
        lines.append(
            f"| {profile} | {_fmt_ms(row.get('normalize_ms'))} | {_fmt_ms(row.get('substance_ms'))} "
            f"| {_fmt_ms(row.get('perm_index_ms'))} | {_fmt_ms(row.get('encode_si_ms'))} "
            f"| {_fmt_ms(row.get('decode_si_ms'))} | {_fmt_ms(row.get('roundtrip_total_ms'))} |"
        )

    lines.extend(
        [
            "",
            "## Width-Gate",
            "",
            "Sweep-Punkte mit `failed_at=width_limit` überspringen `perm_index`, LUT, `encode_si`, `decode_si`.",
            "",
            "---",
            f"_Benchmark-Tool: `python -m tools.profile_benchmark`_",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_report_payload(
    sweep_rows: list[dict[str, Any]],
    *,
    width_skips: int,
    elapsed_seconds: float,
) -> dict[str, Any]:
    limits = derive_profile_limits(
        [r for r in sweep_rows if r.get("section") == "main"]
    )
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_sweep_points": len(sweep_rows),
        "width_skips": width_skips,
        "elapsed_seconds": round(elapsed_seconds, 2),
        "profile_limits": limits,
        "sweep_results": sweep_rows,
    }
