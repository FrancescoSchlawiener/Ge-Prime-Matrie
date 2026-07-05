"""Block-Walk, Checksums, Flatten."""

from __future__ import annotations

import hashlib

from analysis.blocks.node import BlockNode, PointerRef
from analysis.blocks.kinds import PointerKind

MIN_CHAIN_LENGTH = 8


def flatten_sequence(root: BlockNode) -> list[PointerRef]:
    out: list[PointerRef] = []

    def walk(node: BlockNode) -> None:
        out.extend(node.sequence)
        for child in node.children:
            walk(child)

    walk(root)
    return out


def checksum_of_pointer_list(items: list[PointerRef], *, structural_only: bool = False) -> int:
    parts: list[str] = []
    for item in items:
        if structural_only:
            parts.append(item.kind.value)
        else:
            parts.append(f"{item.kind.value}:{item.ptr_id}")
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def sliding_window_checksums(
    items: list[PointerRef],
    *,
    min_len: int = MIN_CHAIN_LENGTH,
    structural_only: bool = False,
) -> list[tuple[int, int, int]]:
    results: list[tuple[int, int, int]] = []
    n = len(items)
    for start in range(n):
        for end in range(start + min_len, n + 1):
            window = items[start:end]
            cs = checksum_of_pointer_list(window, structural_only=structural_only)
            results.append((start, end, cs))
    return results
