"""Pädagogik-Schritte für Compile — Mapping aus CompileStats / Dokument."""

from __future__ import annotations

from analysis.document.model import CompileStats
from analysis.inference.trace import InferenceTrace
from api.schemas.common import Step


def map_nl_compile_steps(stats: CompileStats, trace: InferenceTrace | None = None) -> list[Step]:
    values: dict[str, str | int | float] = {
        "tokens": stats.word_count,
        "skipped": stats.skipped,
    }
    if trace and trace.basis_signature is not None:
        values["prime_count"] = len(trace.basis_signature.prime_set)
    return [
        Step(
            id="compile_nl",
            title="NL-Kompilierung",
            detail="Text → GpmDocument mit Gap-Symmetrie (ein Inferenzlauf).",
            values=values,
        )
    ]


def map_code_compile_steps(language_id: str, registry_count: int) -> list[Step]:
    return [
        Step(
            id="compile_code",
            title="Code-Kompilierung",
            detail=f"Sprache: {language_id}",
            values={"language_id": language_id, "registry_count": registry_count},
        )
    ]


def map_hybrid_compile_steps(segment_count: int, registry_count: int, fence_count: int) -> list[Step]:
    return [
        Step(
            id="compile_hybrid",
            title="Hybrid-Kompilierung",
            detail="Markdown mit Code-Fences — Fences getrennt von Registry.",
            values={
                "segments": segment_count,
                "registry_count": registry_count,
                "fence_count": fence_count,
            },
        )
    ]
