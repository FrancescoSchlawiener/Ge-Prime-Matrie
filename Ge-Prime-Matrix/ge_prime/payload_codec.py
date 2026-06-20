"""Komprimierte API-Payloads für Spans (Spectroscope, cross_analysis)."""

from __future__ import annotations


def _match_token_span(match: dict) -> tuple[int, int]:
    start = int(match.get("token_start", 0))
    if "token_count" in match:
        count = int(match["token_count"])
    elif "token_end" in match:
        count = int(match["token_end"]) - start
    else:
        count = 1
    return start, max(1, count)


def compress_spectro_matches(matches: list[dict]) -> list[dict]:
    """Strip char spans; merge only contiguous token runs with same mode+layer."""
    buckets: dict[tuple[str | None, str | None], list[dict]] = {}
    for match in matches:
        token_start, token_count = _match_token_span(match)
        key = (match.get("mode"), match.get("layer"))
        entry: dict = {
            "mode": match.get("mode"),
            "layer": match.get("layer"),
            "token_start": token_start,
            "token_count": token_count,
        }
        for score_key in ("score", "score_semantic", "score_structural"):
            if score_key in match:
                entry[score_key] = match[score_key]
        buckets.setdefault(key, []).append(entry)

    compressed: list[dict] = []
    for items in buckets.values():
        items.sort(key=lambda row: row["token_start"])
        merged: list[dict] = []
        for item in items:
            if (
                merged
                and merged[-1]["token_start"] + merged[-1]["token_count"] == item["token_start"]
            ):
                prev = merged[-1]
                prev["token_count"] += item["token_count"]
                for score_key in ("score", "score_semantic", "score_structural"):
                    if score_key in item:
                        prev[score_key] = max(prev.get(score_key, 0), item[score_key])
            else:
                merged.append(dict(item))
        compressed.extend(merged)
    compressed.sort(key=lambda row: (row.get("mode") or "", row.get("layer") or "", row["token_start"]))
    return compressed


def compress_rhythm_breaks(breaks: list[dict]) -> list[dict]:
    keys = ("sentence_start", "sentence_count", "line_start", "line_count")
    return [{key: row[key] for key in keys if key in row} for row in breaks]
