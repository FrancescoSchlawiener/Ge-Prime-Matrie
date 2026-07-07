"""Quellcode-Rekonstruktion — nl/col_prefix/EOF-Invariante."""

from __future__ import annotations

from analysis.blocks.kinds import PointerKind
from analysis.blocks.node import BlockLevel, BlockNode
from analysis.blocks.registry import DocumentRegistry
from analysis.blocks.context import ParseDomain
from analysis.code.hybrid import HybridDocument, render_fence_boundary
from analysis.compile.reconstruct import reconstruct_text

INDENT_UNIT = "    "


def _render_value(ref, registry: DocumentRegistry) -> str:
    if ref.kind is PointerKind.S:
        return registry.s_entries[ref.ptr_id].word_canonical
    if ref.kind is PointerKind.N:
        val = registry.n_display(ref.ptr_id)
        if ref.meta.get("bigint"):
            return val + "n"
        return val
    if ref.kind is PointerKind.D:
        if hasattr(registry, "d_display"):
            return registry.d_display(ref.ptr_id)
        return registry.d_entries[ref.ptr_id]
    if ref.kind is PointerKind.C:
        return registry.c_entries[ref.ptr_id].key_bytes.decode("utf-8", errors="replace")
    if ref.kind is PointerKind.H:
        # Pointer-first: aus S/N-Registry über ptr_id rekonstruieren, nicht aus seg.value.
        return registry.reconstruct_h(ref.ptr_id)
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


def _child_by_id(node: BlockNode) -> dict[int, BlockNode]:
    return {child.block_id: child for child in node.children}


def _render_flat_refs(
    refs: list,
    registry: DocumentRegistry,
    depth: int,
    *,
    visual_style: str | None,
) -> str:
    parts: list[str] = []
    for ref in refs:
        child_id = ref.meta.get("child_block_id")
        if ref.kind is PointerKind.SYS and child_id is not None:
            continue
        parts.append(_prefix(ref, depth, visual_style=visual_style))
        parts.append(_render_value(ref, registry))
    return "".join(parts)


def _render_node(node: BlockNode, registry: DocumentRegistry, depth: int = 0) -> str:
    visual = node.meta.get("visual_style")
    parts: list[str] = []
    prefix_nl = node.meta.get("prefix_nl", 0)
    prefix_col = node.meta.get("prefix_col", "")
    if prefix_nl or prefix_col:
        parts.append("\n" * prefix_nl + prefix_col)
    children = _child_by_id(node)
    child_depth = depth + 1 if visual == "indent" else depth
    i = 0
    seq = node.sequence
    while i < len(seq):
        ref = seq[i]
        child_id = ref.meta.get("child_block_id")
        if ref.kind is PointerKind.SYS and child_id is not None:
            child = children.get(child_id)
            if child is not None:
                parts.append(_render_node(child, registry, child_depth))
            i += 1
            continue
        parts.append(_prefix(ref, depth, visual_style=visual))
        parts.append(_render_value(ref, registry))
        i += 1
    return "".join(parts)


def reconstruct_source(module: BlockNode, registry: DocumentRegistry) -> str:
    body = _render_node(module, registry, depth=0)
    trailing = module.meta.get("trailing_whitespace", "")
    return body + trailing


def reconstruct_hybrid(doc: HybridDocument) -> str:
    parts: list[str] = []
    for seg in doc.segments:
        if seg.domain is ParseDomain.NL and seg.nl_document is not None:
            parts.append(reconstruct_text(seg.nl_document))
        elif seg.domain is ParseDomain.CODE:
            if seg.fence_open:
                parts.append(render_fence_boundary(seg.fence_open))
            if seg.code_module is not None and doc.registry is not None:
                parts.append(reconstruct_source(seg.code_module, doc.registry))
            if seg.fence_close:
                parts.append(render_fence_boundary(seg.fence_close))
        if seg.trailing_gap:
            parts.append(seg.trailing_gap)
    if doc.source_trailing:
        parts.append(doc.source_trailing)
    return "".join(parts)
