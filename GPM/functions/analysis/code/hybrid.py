"""Hybrid-Dokument-Modell — Gap-Erhaltungs-Invariante an Fence-Grenzen."""

from __future__ import annotations

from dataclasses import dataclass, field

from alphabets import AlphabetProfile
from analysis.blocks.context import ParseDomain
from analysis.blocks.node import BlockNode
from analysis.blocks.registry import DocumentRegistry
from analysis.document.model import GpmDocument


@dataclass
class FenceBoundary:
    prefix_gap: str
    fence_line: str
    suffix_gap: str = ""


@dataclass
class HybridSegment:
    domain: ParseDomain
    source_start: int
    source_end: int
    language_id: str | None = None
    fence_open: FenceBoundary | None = None
    fence_close: FenceBoundary | None = None
    nl_document: GpmDocument | None = None
    code_module: BlockNode | None = None
    trailing_gap: str = ""


@dataclass
class HybridDocument:
    profile: AlphabetProfile
    segments: list[HybridSegment] = field(default_factory=list)
    registry: DocumentRegistry | None = None
    source_trailing: str = ""


def render_fence_boundary(boundary: FenceBoundary, *, with_newline: bool = True) -> str:
    line = boundary.prefix_gap + boundary.fence_line + boundary.suffix_gap
    if with_newline and not line.endswith("\n"):
        line += "\n"
    return line
