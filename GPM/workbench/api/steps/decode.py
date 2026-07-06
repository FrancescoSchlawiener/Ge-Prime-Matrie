"""Pädagogik-Schritte für Decode — reines Mapping aus InferenceTrace."""

from __future__ import annotations

from analysis.inference.trace import InferenceTrace
from api.schemas.common import Step


def map_decode_steps(trace: InferenceTrace, profile_value: str) -> list[Step]:
    return [
        Step(
            id="decode_si",
            title="S(I)-Dekodierung",
            detail="Aus Substanz und Index wird die Wortsequenz rekonstruiert.",
            values={
                "substance": trace.substance or 0,
                "index": trace.index or 0,
                "word": trace.decoded_word or trace.normalized or "",
            },
            formula="decode(S, I) → Text",
        ),
    ]


def decode_result_from_trace(trace: InferenceTrace, profile_value: str) -> dict:
    return {
        "substance": trace.substance,
        "index": trace.index,
        "word": trace.decoded_word or trace.normalized,
        "profile": profile_value,
    }
