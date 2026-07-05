"""Fraktale Block-Knoten."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from analysis.blocks.kinds import PointerKind


class BlockLevel(str, Enum):
    DOCUMENT = "document"
    PARAGRAPH = "paragraph"
    SENTENCE = "sentence"
    CELL = "cell"
    MODULE = "module"
    CODE_BLOCK = "code_block"


@dataclass(frozen=True)
class TokenSpan:
    token_start: int
    token_count: int

    @property
    def token_end(self) -> int:
        return self.token_start + self.token_count


@dataclass
class PointerRef:
    kind: PointerKind
    ptr_id: int
    nl: int = 0
    col_prefix: str = ""
    meta: dict = field(default_factory=dict)


@dataclass
class BlockNode:
    block_id: int
    level: BlockLevel
    token_span: TokenSpan | None = None
    children: list[BlockNode] = field(default_factory=list)
    sequence: list[PointerRef] = field(default_factory=list)
    perm_index: int = 0
    perm_space: int = 1
    parent_id: int | None = None
    meta: dict = field(default_factory=dict)
