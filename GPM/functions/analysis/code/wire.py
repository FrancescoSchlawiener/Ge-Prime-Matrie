"""Code-Modul-Wire — Blockbaum v2 + volle Code-Registry (S/N/D/C/H)."""

from __future__ import annotations

import struct

from alphabets import AlphabetProfile
from analysis.blocks.codec import decode_block_tree_v2, encode_block_tree_v2
from analysis.code.envelope import BlockEnvelope
from analysis.blocks.context import COrigin, ParseContext, ParseDomain
from analysis.blocks.node import BlockNode
from analysis.blocks.registry import DocumentRegistry, DCodeEntry, StructureEntry
from analysis.document.model import GpmHeaderEntry
from gpm_types.di.codec import decode_di_relation
from gpm_types.di.relation import parse_decimal
from gpm_types.hi.codec import decode_hi
from gpm_types.hi.segments import HiPayload, HiSegment

CODE_WIRE_VERSION = 3


def _pack_utf16(text: str) -> bytes:
    raw = text.encode("utf-8")
    return struct.pack("<I", len(raw)) + raw


def _unpack_utf16(data: bytes, offset: int) -> tuple[str, int]:
    (length,) = struct.unpack_from("<I", data, offset)
    offset += 4
    text = data[offset : offset + length].decode("utf-8")
    return text, offset + length


def encode_code_registry(reg: DocumentRegistry) -> bytes:
    profile = reg.profile.value if hasattr(reg.profile, "value") else str(reg.profile)
    parts = [_pack_utf16(profile)]
    parts.append(struct.pack("<I", len(reg.s_entries)))
    for entry in reg.s_entries:
        parts.append(_pack_utf16(entry.word_canonical))
        parts.append(_pack_utf16(entry.word_normalized))
        parts.append(struct.pack("<QQ", entry.substance & 0xFFFFFFFFFFFFFFFF, entry.perm_index & 0xFFFFFFFFFFFFFFFF))
    parts.append(struct.pack("<I", len(reg.n_entries)))
    for i in range(len(reg.n_entries)):
        parts.append(_pack_utf16(reg.n_display(i)))
    parts.append(struct.pack("<I", len(reg.d_entries)))
    for entry in reg.d_entries:
        if isinstance(entry, DCodeEntry):
            raw = entry.display
            rel = parse_decimal(raw)
            rel_key = entry.relation_key
        else:
            raw = str(entry)
            rel = parse_decimal(raw)
            rel_key = raw
        parts.append(_pack_utf16(raw))
        parts.append(_pack_utf16(decode_di_relation(rel)))
        if isinstance(entry, DCodeEntry):
            parts.append(
                struct.pack(
                    "<III",
                    reg.n_val(entry.whole_ptr),
                    reg.n_val(entry.den_reduced_ptr),
                    reg.n_val(entry.ggt_ptr),
                )
            )
        else:
            parts.append(struct.pack("<III", rel.whole, rel.den_reduced, rel.ggt))
        parts.append(_pack_utf16(rel_key))
    parts.append(struct.pack("<I", len(reg.c_entries)))
    for entry in reg.c_entries:
        origin = entry.origin.value if hasattr(entry.origin, "value") else str(entry.origin)
        origin_b = origin.encode("ascii")
        parts.append(struct.pack("<B", len(origin_b)))
        parts.append(origin_b)
        parts.append(_pack_utf16(entry.key_bytes.decode("utf-8", errors="replace")))
    parts.append(struct.pack("<I", len(reg.h_entries)))
    for payload in reg.h_entries:
        raw = decode_hi(payload)
        parts.append(_pack_utf16(raw))
        parts.append(struct.pack("<H", len(payload.segments)))
        for seg in payload.segments:
            tag_b = seg.tag.encode("ascii")
            parts.append(struct.pack("<B", len(tag_b)))
            parts.append(tag_b)
            parts.append(_pack_utf16(seg.value))
    return b"".join(parts)


def decode_code_registry(data: bytes) -> DocumentRegistry:
    profile, offset = _unpack_utf16(data, 0)
    reg = DocumentRegistry(profile=AlphabetProfile(profile))
    (s_count,) = struct.unpack_from("<I", data, offset)
    offset += 4
    for _ in range(s_count):
        canon, offset = _unpack_utf16(data, offset)
        norm, offset = _unpack_utf16(data, offset)
        substance, perm_index = struct.unpack_from("<QQ", data, offset)
        offset += 16
        reg.s_entries.append(
            GpmHeaderEntry(
                word_id=len(reg.s_entries),
                word_canonical=canon,
                word_normalized=norm,
                substance=substance,
                perm_index=perm_index,
            )
        )
        reg._s_reverse[canon] = len(reg.s_entries) - 1
    (n_count,) = struct.unpack_from("<I", data, offset)
    offset += 4
    wire_ctx = ParseContext(domain=ParseDomain.CODE, language_id="__wire__")
    for _ in range(n_count):
        value, offset = _unpack_utf16(data, offset)
        reg.intern_n_from_display(value, context=wire_ctx)
    (d_count,) = struct.unpack_from("<I", data, offset)
    offset += 4
    for _ in range(d_count):
        raw, offset = _unpack_utf16(data, offset)
        _display, offset = _unpack_utf16(data, offset)
        whole, den_reduced, ggt = struct.unpack_from("<III", data, offset)
        offset += 12
        rel_key, offset = _unpack_utf16(data, offset)
        entry = DCodeEntry(
            display=raw,
            relation_key=rel_key,
            whole_ptr=reg.intern_n_from_display(str(whole), context=wire_ctx),
            den_reduced_ptr=reg.intern_n_from_display(str(den_reduced), context=wire_ctx),
            ggt_ptr=reg.intern_n_from_display(str(ggt), context=wire_ctx),
        )
        reg.d_entries.append(entry)
        reg._d_reverse[rel_key] = len(reg.d_entries) - 1
    (c_count,) = struct.unpack_from("<I", data, offset)
    offset += 4
    for _ in range(c_count):
        (origin_len,) = struct.unpack_from("<B", data, offset)
        offset += 1
        origin = COrigin(data[offset : offset + origin_len].decode("ascii"))
        offset += origin_len
        value, offset = _unpack_utf16(data, offset)
        key = value.encode("utf-8")
        rev_key = (origin, key)
        entry_id = len(reg.c_entries)
        reg.c_entries.append(
            StructureEntry(
                entry_id=entry_id,
                key_bytes=key,
                substance=1,
                perm_index=1,
                perm_space=1,
                origin=origin,
            )
        )
        reg._c_reverse[rev_key] = entry_id
    (h_count,) = struct.unpack_from("<I", data, offset)
    offset += 4
    for _ in range(h_count):
        raw, offset = _unpack_utf16(data, offset)
        (seg_count,) = struct.unpack_from("<H", data, offset)
        offset += 2
        segments: list[HiSegment] = []
        for _ in range(seg_count):
            (tag_len,) = struct.unpack_from("<B", data, offset)
            offset += 1
            tag = data[offset : offset + tag_len].decode("ascii")
            offset += tag_len
            value, offset = _unpack_utf16(data, offset)
            segments.append(HiSegment(tag, value))
        reg.h_entries.append(HiPayload(tuple(segments)))
        reg._h_reverse[raw] = len(reg.h_entries) - 1
    return reg


def encode_code_module(module: BlockNode, registry: DocumentRegistry) -> bytes:
    block_bytes = encode_block_tree_v2(module)
    registry_bytes = encode_code_registry(registry)
    return (
        struct.pack("<BII", CODE_WIRE_VERSION, len(block_bytes), len(registry_bytes))
        + block_bytes
        + registry_bytes
    )


def decode_code_module(data: bytes) -> tuple[BlockNode, DocumentRegistry]:
    (version, block_len, reg_len) = struct.unpack_from("<BII", data, 0)
    if version != CODE_WIRE_VERSION:
        raise ValueError(f"Code-Wire-Version {version} nicht unterstützt")
    offset = 9
    block_end = offset + block_len
    module = decode_block_tree_v2(data[offset:block_end])
    registry = decode_code_registry(data[block_end : block_end + reg_len])
    return module, registry
