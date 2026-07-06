"""DTW-Vergleich von Hierarchie-Ebenen."""

from __future__ import annotations

from analysis.algebra.i_metrics import i_ratio_distance, i_ratio_similarity
from analysis.algebra.substance_kernel import coupled_point_distance, substance_ggt_kgv_similarity
from analysis.geom.dtw import dtw_result_payload, dtw_similarity


def _node_distance(a: dict, b: dict, *, ratio_key: str) -> float:
    i_sim = i_ratio_similarity(a[ratio_key], b[ratio_key])
    s_sim = substance_ggt_kgv_similarity(a.get("s_level", 1), b.get("s_level", 1))
    return coupled_point_distance(i_sim, s_sim)


def compare_level_sequences(seq_a: list[dict], seq_b: list[dict], *, ratio_key: str) -> dict:
    if not seq_a or not seq_b:
        return {
            "geometry_score": 0.0,
            "dtw_cost": None,
            "dtw_failed": True,
            "dtw_window": 0,
            "method": "dtw",
            "length_a": len(seq_a),
            "length_b": len(seq_b),
        }

    def dist(a, b):
        return _node_distance(a, b, ratio_key=ratio_key)

    dtw = dtw_similarity(seq_a, seq_b, dist)
    payload = dtw_result_payload(dtw)
    return {
        "method": "dtw",
        "length_a": len(seq_a),
        "length_b": len(seq_b),
        **payload,
    }
