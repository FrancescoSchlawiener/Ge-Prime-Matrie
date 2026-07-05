"""Wire-Codec für PointerRef und BlockNode (v9-Vorbereitung)."""

from __future__ import annotations

import struct

from analysis.blocks.kinds import PointerKind
from analysis.blocks.node import BlockLevel, BlockNode, PointerRef


def pointer_ref_to_wire(ref: PointerRef) -> bytes:
    kind_b = ref.kind.value.encode("ascii")
    col = ref.col_prefix.encode("utf-8")
    return struct.pack("<BIIH", len(kind_b), ref.ptr_id, ref.nl, len(col)) + kind_b + col


def wire_to_pointer_ref(data: bytes, offset: int = 0) -> tuple[PointerRef, int]:
    kind_len, ptr_id, nl, col_len = struct.unpack_from("<BIIH", data, offset)
    offset += 11
    kind = PointerKind(data[offset : offset + kind_len].decode("ascii"))
    offset += kind_len
    col = data[offset : offset + col_len].decode("utf-8")
    offset += col_len
    return PointerRef(kind=kind, ptr_id=ptr_id, nl=nl, col_prefix=col), offset


def encode_block_tree(root: BlockNode) -> bytes:
    nodes: list[BlockNode] = []

    def walk(n: BlockNode) -> None:
        nodes.append(n)
        for c in n.children:
            walk(c)

    walk(root)
    parts = [struct.pack("<I", len(nodes))]
    for node in nodes:
        level_b = node.level.value.encode("utf-8")
        trail = node.meta.get("trailing_whitespace", "").encode("utf-8")
        parts.append(
            struct.pack("<IIHH", node.block_id, node.parent_id or 0xFFFFFFFF, len(level_b), len(trail))
        )
        parts.append(level_b)
        parts.append(trail)
        parts.append(struct.pack("<H", len(node.sequence)))
        for ref in node.sequence:
            parts.append(pointer_ref_to_wire(ref))
    return b"".join(parts)


def decode_block_tree(data: bytes) -> BlockNode:
    (count,) = struct.unpack_from("<I", data, 0)
    offset = 4
    nodes: dict[int, BlockNode] = {}
    root: BlockNode | None = None
    for _ in range(count):
        block_id, parent_id, level_len, trail_len = struct.unpack_from("<IIHH", data, offset)
        offset += 12
        level = BlockLevel(data[offset : offset + level_len].decode("utf-8"))
        offset += level_len
        trail = data[offset : offset + trail_len].decode("utf-8")
        offset += trail_len
        (seq_len,) = struct.unpack_from("<H", data, offset)
        offset += 2
        seq: list[PointerRef] = []
        for _ in range(seq_len):
            ref, offset = wire_to_pointer_ref(data, offset)
            seq.append(ref)
        node = BlockNode(
            block_id=block_id,
            level=level,
            parent_id=None if parent_id == 0xFFFFFFFF else parent_id,
            sequence=seq,
            meta={"trailing_whitespace": trail} if trail else {},
        )
        nodes[block_id] = node
        if parent_id != 0xFFFFFFFF and parent_id in nodes:
            nodes[parent_id].children.append(node)
        if root is None or level is BlockLevel.MODULE:
            root = node
    return root or BlockNode(block_id=0, level=BlockLevel.MODULE)
