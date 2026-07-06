"""Leichtgewichtiger Trace für Pädagogik ohne Re-Inferenz."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from analysis.basis.signature import BasisSignature
    from analysis.document.model import CompileStats


@dataclass
class InferenceTrace:
    normalized: str | None = None
    substance: int | None = None
    index: int | None = None
    prime_factors: dict[int, int] | None = None
    compile_stats: CompileStats | None = None
    basis_signature: BasisSignature | None = None
    tier_audit: list[dict[str, Any]] = field(default_factory=list)
    raw_word: str | None = None
    decoded_word: str | None = None
