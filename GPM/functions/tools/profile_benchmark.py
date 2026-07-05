"""CLI — Voll-Sweep Profil-Performance- und Grenz-Benchmark."""

from __future__ import annotations

import sys
import time
from collections import Counter
from collections.abc import Callable
from pathlib import Path
from statistics import median
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from alphabets.normalize import prepare_substrate
from alphabets.profiles import AlphabetProfile
from alphabets.registry import all_profiles, lex_order_for_profile, prime_map_for_profile
from gpm_types.si.codec import decode_si, encode_si
from perm.lut import MAX_LUT_BUILD_LENGTH, build_permutation_lut
from perm.multiset import calc_total_perms, perm_fits_width, perm_index
from tools.benchmark_patterns import (
    DUPLICATE_MATRIX_LENGTHS,
    PATTERN_IDS,
    SWEEP_LENGTHS,
    alphabet_for_profile,
    build_all_same_k,
    build_pattern,
    can_build_pattern,
)
from tools.benchmark_report import (
    DEFAULT_OUTPUT_DIR,
    build_report_payload,
    write_json_report,
    write_markdown_report,
)

WIDTH_MAX_BYTES = 16
MAX_LUT_BENCHMARK_N = 10_000
MAX_PERM_INDEX_BENCHMARK_N = 1_000_000
TIMING_WARMUP = 1
TIMING_REPEATS = 5

SKIPPED_EXPENSIVE = ("perm_index", "lut_build", "encode_si", "decode_si")


def _median_ms(fn: Callable[[], None], *, warmup: int = TIMING_WARMUP, repeats: int = TIMING_REPEATS) -> float:
    for _ in range(warmup):
        fn()
    samples: list[float] = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        fn()
        samples.append((time.perf_counter() - t0) * 1000.0)
    return float(median(samples))


def _substance_from_prepared(seq: str, profile: AlphabetProfile) -> int:
    prime_map = prime_map_for_profile(profile)
    s = 1
    for char in seq:
        s *= prime_map[char]
    return s


def width_gate_blocks(n_perm: int, max_bytes: int = WIDTH_MAX_BYTES) -> bool:
    """True wenn teure Perm-Schritte übersprungen werden müssen."""
    if n_perm < 1:
        return True
    if n_perm.bit_length() > max_bytes * 8:
        return True
    if n_perm > MAX_PERM_INDEX_BENCHMARK_N:
        return True
    return not perm_fits_width(n_perm, max_bytes=max_bytes)


def width_gate_reason(n_perm: int, max_bytes: int = WIDTH_MAX_BYTES) -> str:
    if n_perm < 1:
        return "width_limit"
    if n_perm.bit_length() > max_bytes * 8:
        return "width_limit"
    if n_perm > MAX_PERM_INDEX_BENCHMARK_N:
        return "perm_index_limit"
    if not perm_fits_width(n_perm, max_bytes=max_bytes):
        return "width_limit"
    return ""


def run_sweep_point(
    profile: AlphabetProfile,
    raw: str,
    *,
    length: int,
    pattern: str,
    section: str = "main",
    multiplicity_k: int | None = None,
    timed: bool = True,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "profile": profile.name,
        "profile_value": profile.value,
        "length": length,
        "pattern": pattern,
        "section": section,
        "alphabet_size": len(alphabet_for_profile(profile)),
        "multiplicity_k": multiplicity_k,
    }

    def _time_step(fn: Callable[[], None]) -> float:
        if timed:
            return _median_ms(fn)
        fn()
        return 0.0

    try:
        prep_ms = _time_step(lambda: prepare_substrate(raw, profile))
        seq = prepare_substrate(raw, profile)
        row["normalize_ms"] = prep_ms if timed else None
        row["prepare_substrate_ms"] = prep_ms if timed else None
        row["prepared_length"] = len(seq)

        if not seq:
            row.update(
                {
                    "failed_at": "empty_substrate",
                    "encode_ok": False,
                    "decode_ok": False,
                    "roundtrip_ok": False,
                }
            )
            return row

        substance_ms = _time_step(lambda: _substance_from_prepared(seq, profile))
        row["substance_ms"] = substance_ms if timed else None

        counts = Counter(seq)
        n_perm = calc_total_perms(counts)
        row["N_perm"] = n_perm
        row["perm_fits_2"] = perm_fits_width(n_perm, max_bytes=2)
        row["perm_fits_4"] = perm_fits_width(n_perm, max_bytes=4)
        row["perm_fits_8"] = perm_fits_width(n_perm, max_bytes=8)
        row["perm_fits_16"] = perm_fits_width(n_perm, max_bytes=16)

        if width_gate_blocks(n_perm):
            row.update(
                {
                    "failed_at": width_gate_reason(n_perm),
                    "encode_ok": False,
                    "decode_ok": False,
                    "roundtrip_ok": False,
                    "lut_eligible": False,
                    "lut_build_ok": False,
                    "skipped_steps": list(SKIPPED_EXPENSIVE),
                    "perm_index_ms": None,
                    "encode_si_ms": None,
                    "decode_si_ms": None,
                    "lut_build_ms": None,
                    "roundtrip_total_ms": None,
                }
            )
            return row

        lex = lex_order_for_profile(profile)
        seq_list = list(seq)

        def _perm() -> None:
            perm_index(seq_list, counts, lex_order=lex)

        row["perm_index_ms"] = _time_step(_perm)

        lut_eligible = (
            length <= MAX_LUT_BUILD_LENGTH
            and n_perm <= MAX_LUT_BENCHMARK_N
            and row["perm_fits_16"]
        )
        row["lut_eligible"] = lut_eligible
        row["lut_build_ok"] = False
        row["lut_build_ms"] = None

        if lut_eligible:
            try:

                def _lut() -> None:
                    build_permutation_lut(counts, lex_order=lex)

                row["lut_build_ms"] = _time_step(_lut)
                build_permutation_lut(counts, lex_order=lex)
                row["lut_build_ok"] = True
            except Exception as exc:
                row["lut_error"] = f"{type(exc).__name__}: {exc}"

        encoded: tuple[int, int] | None = None

        def _encode() -> None:
            nonlocal encoded
            encoded = encode_si(raw, profile)

        row["encode_si_ms"] = _time_step(_encode)
        encoded = encode_si(raw, profile)
        row["encode_ok"] = True

        def _decode() -> None:
            assert encoded is not None
            decode_si(encoded[0], encoded[1], profile)

        row["decode_si_ms"] = _time_step(_decode)
        decoded = decode_si(encoded[0], encoded[1], profile)
        row["decode_ok"] = True
        row["roundtrip_ok"] = decoded == seq
        if not row["roundtrip_ok"]:
            row["failed_at"] = "roundtrip_mismatch"

        def _roundtrip() -> None:
            s, idx = encode_si(raw, profile)
            decode_si(s, idx, profile)

        row["roundtrip_total_ms"] = _time_step(_roundtrip)

    except Exception as exc:
        row["encode_ok"] = row.get("encode_ok", False)
        row["decode_ok"] = row.get("decode_ok", False)
        row["roundtrip_ok"] = False
        row["error"] = f"{type(exc).__name__}: {exc}"
        if "failed_at" not in row:
            row["failed_at"] = "encode" if not row.get("encode_ok") else "decode"

    return row


def _run_duplicate_matrix(profile: AlphabetProfile) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    lex = alphabet_for_profile(profile)
    for length in DUPLICATE_MATRIX_LENGTHS:
        for k in range(1, length + 1):
            raw = build_all_same_k(lex, length, k)
            if raw is None:
                continue
            rows.append(
                run_sweep_point(
                    profile,
                    raw,
                    length=length,
                    pattern="all_same_k",
                    section="duplicate_matrix",
                    multiplicity_k=k,
                    timed=False,
                )
            )
    return rows


def run_full_benchmark(*, verbose: bool = True) -> dict[str, Any]:
    t0 = time.perf_counter()
    sweep_rows: list[dict[str, Any]] = []
    width_skips = 0
    profiles = all_profiles()
    total = len(profiles)

    for pi, profile in enumerate(profiles, start=1):
        for length in SWEEP_LENGTHS:
            for pattern in PATTERN_IDS:
                if not can_build_pattern(profile, length, pattern):
                    continue
                raw = build_pattern(profile, length, pattern)
                if verbose:
                    print(
                        f"[{pi}/{total}] {profile.name} L={length} {pattern} ...",
                        flush=True,
                    )
                row = run_sweep_point(
                    profile,
                    raw,
                    length=length,
                    pattern=pattern,
                    section="main",
                )
                if row.get("failed_at") == "width_limit":
                    width_skips += 1
                sweep_rows.append(row)

        if verbose:
            print(f"[{pi}/{total}] {profile.name} duplicate_matrix ...", flush=True)
        sweep_rows.extend(_run_duplicate_matrix(profile))

    elapsed = time.perf_counter() - t0
    return build_report_payload(
        sweep_rows,
        width_skips=width_skips,
        elapsed_seconds=elapsed,
    )


def main() -> int:
    out_dir = DEFAULT_OUTPUT_DIR
    if verbose := True:
        print("Profil-Benchmark Voll-Sweep startet ...", flush=True)
    payload = run_full_benchmark(verbose=verbose)
    json_path = out_dir / "benchmark_results.json"
    md_path = out_dir / "PROFILE_LIMITS.md"
    write_json_report(payload, json_path)
    write_markdown_report(
        {
            "generated_at": payload["generated_at"],
            "total_sweep_points": payload["total_sweep_points"],
            "width_skips": payload["width_skips"],
        },
        payload["profile_limits"],
        payload["sweep_results"],
        md_path,
    )
    print(
        f"Fertig in {payload['elapsed_seconds']}s — "
        f"{payload['total_sweep_points']} Punkte, "
        f"{payload['width_skips']} width_limit-Skips",
        flush=True,
    )
    print(f"JSON: docs/benchmark/benchmark_results.json", flush=True)
    print(f"MD:   docs/benchmark/PROFILE_LIMITS.md", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
