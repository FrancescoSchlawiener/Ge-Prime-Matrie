"""Statischer Intervall-Index — Segmentbaum für Stabbing-Queries in O(log n + k)."""

from __future__ import annotations

from dataclasses import dataclass, field

from analysis.blocks.node import TokenSpan
from analysis.hierarchy.geom import DocumentHierarchy, HierarchyNode, intervals_overlap

BITSET_TOKEN_LIMIT = 4096


def _span_mask(start: int, count: int, n: int) -> int:
    mask = 0
    end = min(start + count, n)
    for i in range(max(0, start), end):
        mask |= 1 << i
    return mask


def _masks_overlap(a: int, b: int) -> bool:
    return bool(a & b)


@dataclass
class _LayerIndex:
    n: int
    _tree: list[list[int]] = field(default_factory=list)
    _nodes: list[HierarchyNode] = field(default_factory=list)
    _bitmasks: list[int] | None = None

    def __post_init__(self) -> None:
        if self.n <= 0:
            self.n = 1
        size = 4 * self.n
        self._tree = [[] for _ in range(size)]

    def _add(self, node_idx: int, tree_node: int, left: int, right: int, ql: int, qr: int) -> None:
        if ql > right or qr < left:
            return
        if ql <= left and right <= qr:
            self._tree[tree_node].append(node_idx)
            return
        mid = (left + right) // 2
        self._add(node_idx, tree_node * 2, left, mid, ql, qr)
        self._add(node_idx, tree_node * 2 + 1, mid + 1, right, ql, qr)

    def insert(self, node_idx: int, start: int, count: int) -> None:
        if count <= 0:
            return
        end = start + count - 1
        if end >= self.n:
            end = self.n - 1
        if start > end:
            return
        self._add(node_idx, 1, 0, self.n - 1, start, end)

    def _query(
        self,
        tree_node: int,
        left: int,
        right: int,
        qs: int,
        qe: int,
        out: set[int],
    ) -> None:
        if qs > right or qe < left:
            return
        out.update(self._tree[tree_node])
        if left == right:
            return
        mid = (left + right) // 2
        self._query(tree_node * 2, left, mid, qs, qe, out)
        self._query(tree_node * 2 + 1, mid + 1, right, qs, qe, out)

    def query(self, span: TokenSpan) -> list[HierarchyNode]:
        if not self._nodes:
            return []
        qs = span.token_start
        qe = span.token_end - 1
        if qe < qs:
            return []
        qe = min(qe, self.n - 1)
        qs = max(0, qs)
        query_mask = (
            _span_mask(span.token_start, span.token_count, self.n)
            if self._bitmasks is not None
            else 0
        )
        hits: set[int] = set()
        self._query(1, 0, self.n - 1, qs, qe, hits)
        result: list[HierarchyNode] = []
        for i in sorted(hits):
            if self._bitmasks is not None and not _masks_overlap(query_mask, self._bitmasks[i]):
                continue
            node = self._nodes[i]
            if intervals_overlap(
                node.token_start,
                node.token_count,
                span.token_start,
                span.token_count,
            ):
                result.append(node)
        return result


@dataclass
class IntervalIndex:
    token_count: int
    phrase: _LayerIndex = field(default_factory=lambda: _LayerIndex(1))
    sentence: _LayerIndex = field(default_factory=lambda: _LayerIndex(1))
    paragraph: _LayerIndex = field(default_factory=lambda: _LayerIndex(1))
    line: _LayerIndex = field(default_factory=lambda: _LayerIndex(1))
    page: _LayerIndex = field(default_factory=lambda: _LayerIndex(1))

    def query(self, level: str, span: TokenSpan) -> list[HierarchyNode]:
        layer = getattr(self, level, None)
        if layer is None:
            raise ValueError(f"Unbekannte Ebene: {level}")
        return layer.query(span)


def _build_layer(token_count: int, nodes: list[HierarchyNode]) -> _LayerIndex:
    layer = _LayerIndex(max(1, token_count))
    layer._nodes = list(nodes)
    for idx, node in enumerate(nodes):
        layer.insert(idx, node.token_start, node.token_count)
    if token_count <= BITSET_TOKEN_LIMIT:
        layer._bitmasks = [
            _span_mask(node.token_start, node.token_count, layer.n) for node in nodes
        ]
    return layer


def build_interval_index(hierarchy: DocumentHierarchy, token_count: int) -> IntervalIndex:
    return IntervalIndex(
        token_count=token_count,
        phrase=_build_layer(token_count, hierarchy.semantic.phrases),
        sentence=_build_layer(token_count, hierarchy.semantic.sentences),
        paragraph=_build_layer(token_count, hierarchy.semantic.paragraphs),
        line=_build_layer(token_count, hierarchy.structural.lines),
        page=_build_layer(token_count, hierarchy.structural.pages),
    )


def nodes_intersecting_indexed(
    index: IntervalIndex | None,
    level: str,
    nodes: list[HierarchyNode],
    span: TokenSpan,
) -> list[HierarchyNode]:
    if index is not None:
        return index.query(level, span)
    return [
        n
        for n in nodes
        if intervals_overlap(n.token_start, n.token_count, span.token_start, span.token_count)
    ]
