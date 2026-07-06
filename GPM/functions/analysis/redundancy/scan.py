"""Redundancy analysis — Toy-Modi, index-only Ketten."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from analysis.document.model import GpmDocument
from analysis.index.substance_index import get_substance_index, scan_windows, window_fingerprint

ProgressCallback = Callable[[str, int, str], None]

ADAPTIVE_WIDTHS = (8, 12, 16, 20, 24, 28)


def _registry_ids_for_span(document: GpmDocument, start: int, end: int) -> list[int]:
    if not document.tokens:
        return []
    return [document.tokens[i].word_id for i in range(start, min(end, len(document.tokens)))]


def _structural_fingerprint(document: GpmDocument, start: int, end: int) -> tuple:
    kinds = tuple(
        document.tokens[i].payload_kind.value if hasattr(document.tokens[i].payload_kind, "value") else str(document.tokens[i].payload_kind)
        for i in range(start, min(end, len(document.tokens)))
    )
    return kinds


def _widths_for_scan(
    *,
    window_mode: str,
    window_min: int,
    window_max: int,
    window_size: int,
    token_count: int,
) -> list[int]:
    if window_mode == "adaptive":
        return [w for w in ADAPTIVE_WIDTHS if window_min <= w <= min(window_max, token_count)]
    if window_size > 0:
        w = min(max(window_size, window_min), window_max, token_count)
        return [w] if w >= 2 else []
    w_min = max(2, window_min)
    w_max = min(window_max, token_count)
    if w_min > w_max:
        w_min = w_max
    return list(range(w_min, w_max + 1))


def scan_redundancy(
    document: GpmDocument,
    *,
    canonical: bool = False,
    window_mode: str = "fixed",
    window_min: int = 8,
    window_max: int = 30,
    window_size: int = 15,
    structural_only: bool = False,
    level: str = "token",
    progress_callback: ProgressCallback | None = None,
) -> dict[str, Any]:
    def _prog(phase: str, pct: int, msg: str) -> None:
        if progress_callback:
            progress_callback(phase, pct, msg)

    if not document.tokens:
        return {
            "chains": [],
            "window_count": 0,
            "token_count": 0,
            "canonical": canonical,
            "summary": {"chain_count": 0, "max_match": 0, "window_modes_used": []},
        }

    _prog("index", 5, "Substance-Index materialisieren …")
    substance_index = get_substance_index(document)
    token_count = len(document.tokens)
    widths = _widths_for_scan(
        window_mode=window_mode,
        window_min=window_min,
        window_max=window_max,
        window_size=window_size,
        token_count=token_count,
    )
    if not widths:
        widths = [min(token_count, max(2, window_min))]

    chains: list[dict] = []
    seen: set[tuple] = set()
    total_steps = sum(max(0, token_count - w + 1) for w in widths)
    step_i = 0

    for width in widths:
        if width > token_count:
            continue
        for start in range(0, token_count - width + 1):
            step_i += 1
            if step_i % 50 == 0:
                pct = 10 + int(80 * step_i / max(total_steps, 1))
                _prog("scan", pct, f"Fenster {width} @ {start} …")
            end = start + width
            if structural_only:
                fp_key = _structural_fingerprint(document, start, end)
                fp = window_fingerprint(substance_index, start, end)
            else:
                fp = window_fingerprint(substance_index, start, end)
                fp_key = fp
            if canonical:
                registry_ids = tuple(_registry_ids_for_span(document, start, end))
                key = (width, start, "c", registry_ids)
            else:
                key = (width, start, "s" if structural_only else "f", hash(str(fp_key)))
            if key in seen:
                continue
            seen.add(key)
            if level == "block" and document.root_block is None:
                continue
            hits = scan_windows(
                substance_index,
                width,
                fp,
                modes=["substance_divisor"],
                skip_start=start,
                profile=document.profile,
            )
            if len(hits) > 1:
                chains.append(
                    {
                        "window_width": width,
                        "token_start": start,
                        "token_end": end,
                        "match_count": len(hits),
                        "registry_ids": _registry_ids_for_span(document, start, end),
                        "hit_positions": [[h["token_start"], h["token_end"]] for h in hits[:10]],
                        "structural_only": structural_only,
                    }
                )

    chains.sort(key=lambda c: (-c["match_count"], c["window_width"]))
    trimmed = chains[:50]
    max_match = max((c["match_count"] for c in trimmed), default=0)
    _prog("done", 100, f"{len(trimmed)} Ketten gefunden")
    return {
        "chains": trimmed,
        "window_count": len(trimmed),
        "token_count": token_count,
        "canonical": canonical,
        "window_mode": window_mode,
        "structural_only": structural_only,
        "summary": {
            "chain_count": len(trimmed),
            "max_match": max_match,
            "window_modes_used": list(widths),
        },
    }
