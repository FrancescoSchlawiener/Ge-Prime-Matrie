"""Wire-Codec für PointerRef und BlockNode (v9-Vorbereitung)."""

from __future__ import annotations

import struct

from analysis.blocks.kinds import PointerKind
from analysis.blocks.node import BlockLevel, BlockNode, PointerRef
from analysis.code.envelope import BlockEnvelope

BLOCK_TREE_V1 = 1
BLOCK_TREE_V2 = 2


def _pack_utf16(text: str) -> bytes:
    raw = text.encode("utf-8")
    return struct.pack("<H", len(raw)) + raw


def _unpack_utf16(data: bytes, offset: int) -> tuple[str, int]:
    (length,) = struct.unpack_from("<H", data, offset)
    offset += 2
    text = data[offset : offset + length].decode("utf-8")
    return text, offset + length


def _pack_utf32(text: str) -> bytes:
    raw = text.encode("utf-8")
    return struct.pack("<I", len(raw)) + raw


def _unpack_utf32(data: bytes, offset: int) -> tuple[str, int]:
    (length,) = struct.unpack_from("<I", data, offset)
    offset += 4
    text = data[offset : offset + length].decode("utf-8")
    return text, offset + length


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


def pointer_ref_to_wire_v2(ref: PointerRef) -> bytes:
    kind_b = ref.kind.value.encode("ascii")
    col = ref.col_prefix.encode("utf-8")
    parts = [struct.pack("<BIIH", len(kind_b), ref.ptr_id, ref.nl, len(col)), kind_b, col]
    meta_flags = 0
    tail: list[bytes] = []
    if ref.meta.get("bigint"):
        meta_flags |= 1
    if ref.meta.get("child_block_id") is not None:
        meta_flags |= 2
        tail.append(struct.pack("<I", int(ref.meta["child_block_id"])))
    if ref.meta.get("close_syntax"):
        meta_flags |= 4
        cs = ref.meta["close_syntax"].encode("utf-8")
        tail.append(struct.pack("<H", len(cs)) + cs)
    parts.append(struct.pack("<B", meta_flags))
    parts.extend(tail)
    return b"".join(parts)


def wire_to_pointer_ref_v2(data: bytes, offset: int = 0) -> tuple[PointerRef, int]:
    kind_len, ptr_id, nl, col_len = struct.unpack_from("<BIIH", data, offset)
    offset += 11
    kind = PointerKind(data[offset : offset + kind_len].decode("ascii"))
    offset += kind_len
    col = data[offset : offset + col_len].decode("utf-8")
    offset += col_len
    (meta_flags,) = struct.unpack_from("<B", data, offset)
    offset += 1
    meta: dict = {}
    if meta_flags & 1:
        meta["bigint"] = True
    if meta_flags & 2:
        (child_id,) = struct.unpack_from("<I", data, offset)
        offset += 4
        meta["child_block_id"] = child_id
    if meta_flags & 4:
        (close_len,) = struct.unpack_from("<H", data, offset)
        offset += 2
        meta["close_syntax"] = data[offset : offset + close_len].decode("utf-8")
        offset += close_len
    return PointerRef(kind=kind, ptr_id=ptr_id, nl=nl, col_prefix=col, meta=meta), offset


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


def encode_block_tree_v2(root: BlockNode) -> bytes:
    nodes: list[BlockNode] = []

    def walk(node: BlockNode) -> None:
        nodes.append(node)
        for child in node.children:
            walk(child)

    walk(root)
    parts = [struct.pack("<BI", BLOCK_TREE_V2, len(nodes))]
    for node in nodes:
        level_b = node.level.value.encode("utf-8")
        trail = node.meta.get("trailing_whitespace", "").encode("utf-8")
        flags = 0
        optional: list[bytes] = []
        env_raw = node.meta.get("envelope")
        if env_raw is not None:
            flags |= 1
            env_val = int(env_raw) if not isinstance(env_raw, BlockEnvelope) else int(env_raw)
            optional.append(struct.pack("<B", env_val))
        elif node.meta.get("visual_style"):
            flags |= 1
            vs = str(node.meta["visual_style"])
            env_map = {
                "tag": BlockEnvelope.TAG,
                "keyword": BlockEnvelope.KEYWORD,
                "indent": BlockEnvelope.INDENT,
                "bracket": BlockEnvelope.BRACKET,
                "brace": BlockEnvelope.BRACE,
            }
            optional.append(struct.pack("<B", int(env_map.get(vs, BlockEnvelope.BRACE))))
        if node.meta.get("open_syntax"):
            flags |= 2
            optional.append(_pack_utf32(str(node.meta["open_syntax"])))
        if node.meta.get("prefix_nl") or node.meta.get("prefix_col"):
            flags |= 4
            optional.append(struct.pack("<H", int(node.meta.get("prefix_nl", 0))))
            optional.append(_pack_utf32(str(node.meta.get("prefix_col", ""))))
        if node.meta.get("rule_language"):
            flags |= 8
            optional.append(_pack_utf32(str(node.meta["rule_language"])))
        if node.meta.get("embedded_language"):
            flags |= 16
            optional.append(_pack_utf32(str(node.meta["embedded_language"])))
        parts.append(
            struct.pack(
                "<IIHHB",
                node.block_id,
                node.parent_id if node.parent_id is not None else 0xFFFFFFFF,
                len(level_b),
                len(trail),
                flags,
            )
        )
        parts.append(level_b)
        parts.append(trail)
        parts.extend(optional)
        parts.append(struct.pack("<H", len(node.sequence)))
        for ref in node.sequence:
            parts.append(pointer_ref_to_wire_v2(ref))
    return b"".join(parts)


def decode_block_tree_v2(data: bytes) -> BlockNode:
    (version,) = struct.unpack_from("<B", data, 0)
    if version != BLOCK_TREE_V2:
        raise ValueError(f"Block-Tree-Version {version} nicht unterstützt (erwartet {BLOCK_TREE_V2})")
    (count,) = struct.unpack_from("<I", data, 1)
    offset = 5
    nodes: dict[int, BlockNode] = {}
    root: BlockNode | None = None
    for _ in range(count):
        block_id, parent_id, level_len, trail_len, flags = struct.unpack_from("<IIHHB", data, offset)
        offset += 13
        level = BlockLevel(data[offset : offset + level_len].decode("utf-8"))
        offset += level_len
        trail = data[offset : offset + trail_len].decode("utf-8")
        offset += trail_len
        meta: dict = {}
        if trail:
            meta["trailing_whitespace"] = trail
        if flags & 1:
            (env_u8,) = struct.unpack_from("<B", data, offset)
            offset += 1
            meta["envelope"] = env_u8
            try:
                env = BlockEnvelope(env_u8)
                meta["visual_style"] = env.name.lower()
                if env is BlockEnvelope.BRACKET:
                    meta["visual_style"] = "bracket"
            except ValueError:
                pass
        if flags & 2:
            open_syntax, offset = _unpack_utf32(data, offset)
            meta["open_syntax"] = open_syntax
        if flags & 4:
            (prefix_nl,) = struct.unpack_from("<H", data, offset)
            offset += 2
            prefix_col, offset = _unpack_utf32(data, offset)
            meta["prefix_nl"] = prefix_nl
            meta["prefix_col"] = prefix_col
        if flags & 8:
            rule_lang, offset = _unpack_utf32(data, offset)
            meta["rule_language"] = rule_lang
        if flags & 16:
            embedded, offset = _unpack_utf32(data, offset)
            meta["embedded_language"] = embedded
        (seq_len,) = struct.unpack_from("<H", data, offset)
        offset += 2
        sequence: list[PointerRef] = []
        for _ in range(seq_len):
            ref, offset = wire_to_pointer_ref_v2(data, offset)
            sequence.append(ref)
        node = BlockNode(
            block_id=block_id,
            level=level,
            parent_id=None if parent_id == 0xFFFFFFFF else parent_id,
            sequence=sequence,
            meta=meta,
        )
        nodes[block_id] = node
        if parent_id != 0xFFFFFFFF and parent_id in nodes:
            nodes[parent_id].children.append(node)
        if root is None or level is BlockLevel.MODULE:
            root = node
    return root or BlockNode(block_id=0, level=BlockLevel.MODULE)
