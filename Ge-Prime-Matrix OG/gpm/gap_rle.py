"""GAP-RLE — kompakter Rest-Whitespace für .gpm v7."""

from __future__ import annotations

import struct

MAX_GAP_RLE_BYTES = 16 * 1024 * 1024
MAX_GAP_STRING_BYTES = 65535


def encode_gap_rle(gap_map: dict[int, str]) -> bytes:
    """Serialisiert {token_index: gap_string} → GAP-RLE-Block."""
    items = sorted(gap_map.items())
    parts = [struct.pack("<I", len(items))]
    for token_index, gap in items:
        raw = gap.encode("utf-8")
        if len(raw) > MAX_GAP_STRING_BYTES:
            raise ValueError(f"Gap an Index {token_index} zu lang.")
        parts.append(struct.pack("<IH", token_index, len(raw)))
        parts.append(raw)
    blob = b"".join(parts)
    if len(blob) > MAX_GAP_RLE_BYTES:
        raise ValueError("GAP-RLE-Block zu groß.")
    return blob


def decode_gap_rle(data: bytes) -> dict[int, str]:
    if not data:
        return {}
    if len(data) < 4:
        raise ValueError("GAP-RLE-Block zu kurz.")
    (count,) = struct.unpack_from("<I", data, 0)
    offset = 4
    result: dict[int, str] = {}
    for _ in range(count):
        if offset + 6 > len(data):
            raise ValueError("GAP-RLE-Eintrag abgeschnitten.")
        token_index, raw_len = struct.unpack_from("<IH", data, offset)
        offset += 6
        if offset + raw_len > len(data):
            raise ValueError("GAP-RLE-Bytes abgeschnitten.")
        result[token_index] = data[offset : offset + raw_len].decode("utf-8")
        offset += raw_len
    if offset != len(data):
        raise ValueError("GAP-RLE enthält überhängende Bytes.")
    return result
