"""API helper types."""

from __future__ import annotations

from typing import Any, TypedDict

from analysis.document.model import CompileStats, GpmDocument
from analysis.inference.trace import InferenceTrace


class InferenceBundle(TypedDict, total=False):
    document: GpmDocument
    stats: CompileStats
    trace: InferenceTrace
    content_hash: str
    cache_hit: bool
    hybrid: Any
