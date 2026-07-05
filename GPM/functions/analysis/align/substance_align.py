"""Substanz-Sequenz-Vergleich via DTW."""

from __future__ import annotations

from analysis.geom.dtw import dtw_similarity
from analysis.substance.compare import substance_ggt_kgv_distance


def compare_substance_sequences(seq_a: list[int], seq_b: list[int]) -> dict:
    result = dtw_similarity(seq_a, seq_b, substance_ggt_kgv_distance)
    return {
        "geometry_score": round(result.similarity, 6),
        "dtw_cost": result.cost,
        "dtw_failed": result.failed,
        "substance_parallel": result.similarity >= 0.9,
    }
