"""Substanz-Ausrichtung — ggT/kgV-Kette entlang der Token-Folge."""

from __future__ import annotations

import math
import statistics

from ge_prime.compare import (
    compare_substances,
    substance_ggt_kgv_distance,
    substance_ggt_kgv_similarity,
    substance_transition_similarity,
)
from ge_prime.diff import classify_word_pair
from ge_prime.dtw import dtw_result_payload, dtw_similarity
from gpm.model import GpmDocument
from pipeline.normalize import apply_case

SUBSTANCE_TWIN_THRESHOLD = 0.85
SUBSTANCE_PARALLEL_THRESHOLD = 0.75
LITERAL_LOW_THRESHOLD = 0.6


def _transition_fields(s_prev: int, s_curr: int) -> dict:
    if s_prev <= 0 or s_curr <= 0:
        return {"ggt": 0, "kgv": 0, "ggt_kgv_ratio": 0.0, "s_ratio": 0.0}
    ggt = math.gcd(s_prev, s_curr)
    kgv = math.lcm(s_prev, s_curr)
    ratio = round(substance_transition_similarity(s_prev, s_curr), 6)
    return {
        "ggt": ggt,
        "kgv": kgv,
        "ggt_kgv_ratio": ratio,
        "s_ratio": ratio,
    }


def extract_substance_curve(document: GpmDocument) -> list[dict]:
    """Pro Token: Substanz, ggT/kgV-Kontinuität zum Vorgänger."""
    explicit_map = dict(document.explicit)
    points: list[dict] = []
    prev_substance: int | None = None

    for position, token in enumerate(document.tokens):
        if position in explicit_map:
            word = explicit_map[position]
            normalized = word.upper()
            substance = document.header[token.word_id].substance if token.word_id < len(document.header) else 1
        else:
            entry = document.header[token.word_id]
            word = apply_case(entry.word_original, token.case_code)
            normalized = entry.word_normalized
            substance = entry.substance

        if prev_substance is None:
            trans = {"ggt": 0, "kgv": 0, "ggt_kgv_ratio": 0.0, "s_ratio": 0.0}
        else:
            trans = _transition_fields(prev_substance, substance)

        points.append(
            {
                "position": position,
                "word": word,
                "normalized": normalized,
                "substance": substance,
                "perm_index": token.perm_index,
                **trans,
            }
        )
        prev_substance = substance

    return points


def _substance_point_distance(a: dict, b: dict) -> float:
    return substance_ggt_kgv_distance(a["substance"], b["substance"])


def _aligned_substance_score(seq_a: list[dict], seq_b: list[dict]) -> float:
    if not seq_a or len(seq_a) != len(seq_b):
        return 0.0
    ratios = [
        substance_ggt_kgv_similarity(a["substance"], b["substance"])
        for a, b in zip(seq_a, seq_b)
    ]
    return sum(ratios) / len(ratios)


def _count_aligned_pairs(seq_a: list[dict], seq_b: list[dict]) -> tuple[int, int]:
    """substance_twin_count, anagram_shadow_count bei gleicher Länge."""
    twins = 0
    anagrams = 0
    if len(seq_a) != len(seq_b):
        return twins, anagrams
    for a, b in zip(seq_a, seq_b):
        sim = substance_ggt_kgv_similarity(a["substance"], b["substance"])
        if sim >= SUBSTANCE_TWIN_THRESHOLD and a["normalized"] != b["normalized"]:
            twins += 1
        pair = classify_word_pair(
            a["substance"],
            b["substance"],
            a["perm_index"],
            b["perm_index"],
        )
        if pair["is_anagram"]:
            anagrams += 1
    return twins, anagrams


def compare_substance_sequences(
    seq_a: list[dict],
    seq_b: list[dict],
    *,
    literal_match_ratio: float = 0.0,
) -> dict:
    """Vergleicht Substanz-Ketten via ggT/kgV-DTW."""
    if not seq_a or not seq_b:
        return {
            "geometry_score": 0.0,
            "aligned": False,
            "substance_twin_count": 0,
            "anagram_shadow_count": 0,
            "substance_parallel": False,
            "method": "dtw",
            "dtw_cost": None,
            "dtw_failed": True,
            "dtw_window": 0,
            "mean_similarity": 0.0,
            "length_a": len(seq_a),
            "length_b": len(seq_b),
        }

    aligned = len(seq_a) == len(seq_b)
    twin_count, anagram_count = _count_aligned_pairs(seq_a, seq_b)
    aligned_score = _aligned_substance_score(seq_a, seq_b) if aligned else 0.0
    dtw = dtw_similarity(seq_a, seq_b, _substance_point_distance)
    dtw_score = dtw.similarity
    geometry_score = max(aligned_score, dtw_score) if aligned else dtw_score

    if aligned:
        sims = [
            substance_ggt_kgv_similarity(a["substance"], b["substance"])
            for a, b in zip(seq_a, seq_b)
        ]
        mean_sim = statistics.mean(sims) if sims else 0.0
    else:
        mean_sim = dtw_score

    substance_parallel = (
        geometry_score >= SUBSTANCE_PARALLEL_THRESHOLD
        and literal_match_ratio < LITERAL_LOW_THRESHOLD
    )

    payload = dtw_result_payload(dtw)
    return {
        "geometry_score": round(geometry_score, 6),
        "aligned": aligned,
        "substance_twin_count": twin_count,
        "anagram_shadow_count": anagram_count,
        "substance_parallel": substance_parallel,
        "method": "dtw",
        "mean_similarity": round(mean_sim, 6),
        "length_a": len(seq_a),
        "length_b": len(seq_b),
        **payload,
    }
