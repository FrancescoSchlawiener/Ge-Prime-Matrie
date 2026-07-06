"""Pädagogik-Schritte für Encode — reines Mapping aus InferenceTrace."""

from __future__ import annotations

from analysis.inference.trace import InferenceTrace
from api.schemas.common import Step


def map_encode_steps(trace: InferenceTrace, profile_value: str) -> list[Step]:
    factors = trace.prime_factors or {}
    return [
        Step(
            id="normalize",
            title="Normalisierung",
            detail="Rohtext wird für das gewählte Alphabetprofil vorbereitet.",
            values={
                "raw": trace.raw_word or "",
                "normalized": trace.normalized or "",
                "profile": profile_value,
            },
        ),
        Step(
            id="encode_si",
            title="S(I)-Kodierung",
            detail="Substanz S (Primprodukt) und Permutations-Index I aus dem Inferenzlauf.",
            values={
                "substance": trace.substance or 0,
                "index": trace.index or 0,
                "prime_factor_count": len(factors),
            },
            formula="S = ∏ pᵢ^aᵢ,  I = rank(Sequenz)",
        ),
    ]


def encode_result_from_trace(trace: InferenceTrace, profile_value: str) -> dict:
    return {
        "word": trace.raw_word or "",
        "normalized": trace.normalized or "",
        "substance": trace.substance,
        "index": trace.index,
        "profile": profile_value,
    }
