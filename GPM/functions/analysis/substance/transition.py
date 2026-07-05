"""Übergangsmetriken zwischen aufeinanderfolgenden Substanzen."""

from __future__ import annotations

from analysis.substance.compare import substance_ggt_kgv_similarity


def transition_fields(s_prev: int, s_curr: int) -> dict:
    sim = substance_ggt_kgv_similarity(s_prev, s_curr)
    return {
        "ggt_kgv_similarity": round(sim, 6),
        "ggt_kgv_distance": round(1.0 - sim, 6),
    }
