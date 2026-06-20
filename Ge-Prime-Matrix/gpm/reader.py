"""Lesen, Dekodieren und Suche in .gpm-Dateien."""

from __future__ import annotations

import math
import struct

from ge_prime.compare import compare_substances, substance_covers, substance_lcm, union_letters
from ge_prime.decode import decode_word
from gpm.format import (
    VERSION,
    VERSION_V6,
    VERSION_V2,
    VERSION_V3,
    VERSION_V4,
    read_file_header_fields,
    read_gpm,
)
from gpm.int_codec import genome_substance_field_bytes, token_byte_len
from gpm.model import GpmAnalysis, GpmDocument
from pipeline.normalize import apply_case
from pipeline.process import process_token

BODY_PREVIEW_LIMIT = 200
HEADER_PREVIEW_LIMIT = 500


def reconstruct_text(document: GpmDocument) -> str:
    """Exakte, verlustfreie Rekonstruktion des Originaltextes."""
    if getattr(document, "gap_rle", None) is not None and getattr(document, "hierarchy", None):
        from gpm.reconstruct_v7 import reconstruct_text_v7

        return reconstruct_text_v7(document)
    if not document.gaps:
        return ""

    explicit_map = dict(document.explicit)
    parts: list[str] = [document.gaps[0]]

    for i, token in enumerate(document.tokens):
        if i in explicit_map:
            word = explicit_map[i]
        else:
            entry = document.header[token.word_id]
            word = apply_case(entry.word_original, token.case_code)
        parts.append(word)
        parts.append(document.gaps[i + 1])

    return "".join(parts)


def decode_document_text(document: GpmDocument) -> str:
    return reconstruct_text(document)


def _header_dict(entry) -> dict:
    return {
        "word_id": entry.word_id,
        "original": entry.word_original,
        "normalized": entry.word_normalized,
        "substance": entry.substance,
    }


def _token_dict(document: GpmDocument, position: int, token) -> dict:
    entry = document.header[token.word_id]
    normalized = decode_word(entry.substance, token.perm_index)
    return {
        "position": position,
        "word_id": token.word_id,
        "perm_index": token.perm_index,
        "original": entry.word_original,
        "normalized": normalized,
        "substance": entry.substance,
    }


def _genome_bytes(document: GpmDocument, *, version: int) -> int:
    total = 0
    for entry in document.header:
        total += 2 + len(entry.word_original.encode("utf-8"))
        total += 2 + len(entry.word_normalized.encode("utf-8"))
        if version >= VERSION_V4:
            total += genome_substance_field_bytes(entry.substance)
        else:
            sub = entry.substance
            sub_len = 1 if sub == 0 else (sub.bit_length() + 7) // 8
            total += 2 + sub_len
    return total


def _body_bytes(document: GpmDocument, *, version: int, data: bytes | None = None) -> int:
    if data is not None and version in (VERSION, VERSION_V6) and len(data) >= 29:
        payload_len = struct.unpack_from("<I", data, 25)[0]
        header_bytes = _genome_bytes(document, version=version)
        _, _, separator_bytes = read_file_header_fields(data)
        explicit_bytes = sum(
            8 + len(text.encode("utf-8")) for _, text in document.explicit
        )
        return max(0, payload_len - header_bytes - separator_bytes - explicit_bytes)
    if version >= VERSION_V4:
        return sum(
            token_byte_len(word_id=token.word_id, header=document.header)
            for token in document.tokens
        )
    return len(document.tokens) * 7


def genome_payload_bytes(document: GpmDocument, *, version: int) -> int:
    """Öffentliche Schätzung der Genom-Nutzlast in Bytes (für size_compare)."""
    return _genome_bytes(document, version=version)


def body_payload_bytes(
    document: GpmDocument, *, version: int, data: bytes | None = None
) -> int:
    """Öffentliche Schätzung der Geometrie-Nutzlast in Bytes (für size_compare)."""
    return _body_bytes(document, version=version, data=data)


def analyze_gpm(data: bytes, *, preview_limit: int = HEADER_PREVIEW_LIMIT) -> GpmAnalysis:
    version, separator_perm, separator_bytes = read_file_header_fields(data)
    document = read_gpm(data)

    header_bytes = _genome_bytes(document, version=version)
    body_bytes = _body_bytes(document, version=version, data=data)
    if version == VERSION_V2:
        separator_bytes = sum(4 + len(g.encode("utf-8")) for g in document.gaps)

    header_rows = [_header_dict(entry) for entry in document.header[:preview_limit]]
    body_preview = [
        _token_dict(document, idx, token)
        for idx, token in enumerate(document.tokens[:BODY_PREVIEW_LIMIT])
    ]

    return GpmAnalysis(
        version=version,
        unique_words=len(document.header),
        total_tokens=len(document.tokens),
        file_bytes=len(data),
        header_bytes=header_bytes,
        body_bytes=body_bytes,
        separator_bytes=separator_bytes,
        separator_perm=separator_perm,
        header=header_rows,
        body_preview=body_preview,
        reconstructed_text=reconstruct_text(document),
        lossless=(version >= VERSION_V3),
    )


def search_by_word(document: GpmDocument, query: str) -> dict:
    processed = process_token(query.strip())
    if processed is None:
        raise ValueError(f"Suchwort ungültig: {query!r}")

    query_substance = processed.substance
    header_hits = [
        _header_dict(entry)
        for entry in document.header
        if entry.substance == query_substance
    ]
    word_ids = {entry["word_id"] for entry in header_hits}
    positions = [
        {
            "position": idx,
            "word_id": token.word_id,
            "perm_index": token.perm_index,
        }
        for idx, token in enumerate(document.tokens)
        if token.word_id in word_ids
    ]

    return {
        "query": query,
        "query_normalized": processed.word_normalized,
        "query_substance": query_substance,
        "found_in_header": len(header_hits) > 0,
        "header_matches": header_hits,
        "occurrences": len(positions),
        "positions": positions[:200],
    }


def search_by_gcd(document: GpmDocument, query: str) -> dict:
    processed = process_token(query.strip())
    if processed is None:
        raise ValueError(f"Suchwort ungültig: {query!r}")

    query_substance = processed.substance
    matches: list[dict] = []

    for entry in document.header:
        gcd_value = math.gcd(entry.substance, query_substance)
        if gcd_value <= 1:
            continue
        cmp = compare_substances(entry.substance, query_substance)
        matches.append(
            {
                **_header_dict(entry),
                "gcd_value": gcd_value,
                "shared_letters": cmp["shared_letters"],
            }
        )

    word_ids = {row["word_id"] for row in matches}
    token_hits = sum(1 for token in document.tokens if token.word_id in word_ids)

    return {
        "query": query,
        "query_substance": query_substance,
        "matches": matches[:200],
        "unique_words": len(matches),
        "token_hits": token_hits,
    }


def search_by_lcm(document: GpmDocument, query1: str, query2: str) -> dict:
    p1 = process_token(query1.strip())
    p2 = process_token(query2.strip())
    if p1 is None:
        raise ValueError(f"Suchwort 1 ungültig: {query1!r}")
    if p2 is None:
        raise ValueError(f"Suchwort 2 ungültig: {query2!r}")

    s1 = p1.substance
    s2 = p2.substance
    lcm_value = substance_lcm(s1, s2)
    union = union_letters(s1, s2)
    matches: list[dict] = []

    for entry in document.header:
        if not substance_covers(entry.substance, lcm_value):
            continue
        matches.append(
            {
                **_header_dict(entry),
                "covers_lcm": True,
            }
        )

    word_ids = {row["word_id"] for row in matches}
    token_hits = sum(1 for token in document.tokens if token.word_id in word_ids)

    return {
        "query": query1,
        "query2": query2,
        "query_normalized": p1.word_normalized,
        "query2_normalized": p2.word_normalized,
        "query_substance": s1,
        "query2_substance": s2,
        "lcm_value": lcm_value,
        "union_letters": union,
        "matches": matches[:200],
        "unique_words": len(matches),
        "token_hits": token_hits,
    }
