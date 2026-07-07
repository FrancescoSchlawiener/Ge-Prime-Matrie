"""Quellcode-Rekonstruktion — nl/col_prefix/EOF-Invariante."""

from __future__ import annotations

from analysis.blocks.kinds import PointerKind
from analysis.blocks.node import BlockLevel, BlockNode
from analysis.blocks.registry import DocumentRegistry
from analysis.code.hybrid import HybridDocument, render_fence_boundary
from analysis.compile.reconstruct import reconstruct_text

INDENT_UNIT = "    "


def _render_value(ref, registry: DocumentRegistry) -> str:
    if ref.kind is PointerKind.S:
        return registry.s_entries[ref.ptr_id].word_canonical
    if ref.kind is PointerKind.N:
        return str(registry.n_entries[ref.ptr_id])
    if ref.kind is PointerKind.D:
        return registry.d_entries[ref.ptr_id]
    if ref.kind is PointerKind.C:
        return registry.c_entries[ref.ptr_id].key_bytes.decode("utf-8", errors="replace")
    if ref.kind is PointerKind.H:
        from gpm_types.hi.codec import decode_hi

        return decode_hi(registry.h_entries[ref.ptr_id])
    if ref.kind is PointerKind.SYS:
        close = ref.meta.get("close_syntax") or registry.c_entries[ref.ptr_id].key_bytes.decode(
            "utf-8", errors="replace"
        )
        return close if close and close != "CLOSE" else ""
    return ""


def _prefix(ref, depth: int, *, visual_style: str | None) -> str:
    parts = ["\n" * ref.nl]
    if ref.col_prefix:
        parts.append(ref.col_prefix)
    elif visual_style == "indent" and ref.nl:
        parts.append(INDENT_UNIT * depth)
    return "".join(parts)


def _render_node(node: BlockNode, registry: DocumentRegistry, depth: int = 0) -> str:
    visual = node.meta.get("visual_style")
    parts: list[str] = []
    prefix_nl = node.meta.get("prefix_nl", 0)
    prefix_col = node.meta.get("prefix_col", "")
    if prefix_nl or prefix_col:
        parts.append("\n" * prefix_nl + prefix_col)
    for ref in node.sequence:
        parts.append(_prefix(ref, depth, visual_style=visual))
        parts.append(_render_value(ref, registry))
    child_depth = depth + 1 if visual == "indent" else depth
    for child in node.children:
        parts.append(_render_node(child, registry, child_depth))
    return "".join(parts)


def reconstruct_source(module: BlockNode, registry: DocumentRegistry) -> str:
    body = _render_node(module, registry, depth=0)
    trailing = module.meta.get("trailing_whitespace", "")
    return body + trailing


def reconstruct_hybrid(doc: HybridDocument) -> str:
    parts: list[str] = []
    for seg in doc.segments:
        if seg.domain.value == "nl" and seg.nl_document is not None:
            parts.append(reconstruct_text(seg.nl_document))
            if seg.trailing_gap:
                parts.append(seg.trailing_gap)
        elif seg.domain.value == "code" and seg.code_module is not None and doc.registry is not None:
            if seg.fence_open is not None:
                parts.append(render_fence_boundary(seg.fence_open))
            parts.append(reconstruct_source(seg.code_module, doc.registry))
            if seg.trailing_gap:
                parts.append(seg.trailing_gap)
            if seg.fence_close is not None:
                parts.append(render_fence_boundary(seg.fence_close))
    if doc.source_trailing:
        parts.append(doc.source_trailing)
    return "".join(parts)
