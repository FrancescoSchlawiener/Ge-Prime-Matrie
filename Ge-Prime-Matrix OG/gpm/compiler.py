"""Text → .gpm Dokument (Compiler, v7 — verlustfrei, GAP-RLE + Hierarchie)."""

from __future__ import annotations

import struct

from gpm.cell_geom import build_document_cells
from gpm.format import FLAG_BODY_CELL, read_file_header_fields, write_gpm
from gpm.hierarchy_geom import build_document_hierarchy
from gpm.int_codec import genome_substance_field_bytes
from gpm.model import GpmCompileStats, GpmDocument, GpmHeaderEntry, GpmToken
from gpm.separator_codec import scan_perm_code
from pipeline.normalize import CASE_EXPLICIT, CASE_LOWER, apply_case, detect_case, normalize_text_nfc
from pipeline.process import process_token
from pipeline.tokenize import split_segments

MAX_COMPILE_TOKENS = 100_000


def _genome_bytes(header: list[GpmHeaderEntry]) -> int:
    total = 0
    for entry in header:
        total += 2 + len(entry.word_original.encode("utf-8"))
        total += 2 + len(entry.word_normalized.encode("utf-8"))
        total += genome_substance_field_bytes(entry.substance)
    return total


def _explicit_bytes(explicit: list[tuple[int, str]]) -> int:
    return sum(8 + len(text.encode("utf-8")) for _, text in explicit)


def compile_text(text: str) -> tuple[GpmDocument, bytes, GpmCompileStats]:
    """
    Parser → S(I) + Schreibweise + Separator-Layer → Binärpacken (v7).

    Perm-Code wird beim Kompilieren aus dem Text berechnet; Tabellen liegen im Code.
    """
    if not text or not text.strip():
        raise ValueError("Leerer Text — nichts zu kompilieren.")

    source = normalize_text_nfc(text)
    segments = split_segments(source)

    dictionary: dict[str, int] = {}
    header: list[GpmHeaderEntry] = []
    tokens: list[GpmToken] = []
    gaps: list[str] = []
    explicit: list[tuple[int, str]] = []

    pending_gap = ""
    skipped = 0
    word_count = 0

    for kind, chunk in segments:
        if kind == "gap":
            pending_gap += chunk
            continue

        if word_count >= MAX_COMPILE_TOKENS:
            raise ValueError(f"Maximal {MAX_COMPILE_TOKENS:,} Wörter pro .gpm.")

        processed = process_token(chunk, source="gpm")
        if processed is None:
            pending_gap += chunk
            skipped += 1
            continue

        canonical = apply_case(chunk, CASE_LOWER)
        if canonical not in dictionary:
            word_id = len(header)
            dictionary[canonical] = word_id
            header.append(
                GpmHeaderEntry(
                    word_id=word_id,
                    word_original=canonical,
                    word_normalized=processed.word_normalized,
                    substance=processed.substance,
                )
            )
        word_id = dictionary[canonical]

        code = detect_case(chunk)
        token_index = len(tokens)

        gaps.append(pending_gap)
        pending_gap = ""

        tokens.append(
            GpmToken(
                word_id=word_id,
                perm_index=processed.perm_index,
                case_code=code,
            )
        )
        if code == CASE_EXPLICIT:
            explicit.append((token_index, chunk))

        word_count += 1

    gaps.append(pending_gap)

    if not tokens:
        raise ValueError("Kein Wort konnte encodiert werden.")

    draft = GpmDocument(header=header, tokens=tokens, gaps=gaps, explicit=explicit)
    cells = build_document_cells(draft)
    hierarchy = build_document_hierarchy(draft)
    document = GpmDocument(
        header=header,
        tokens=tokens,
        gaps=gaps,
        explicit=explicit,
        cells=cells,
        hierarchy=hierarchy,
    )
    from ge_prime.substance_index import build_substance_index
    from gpm.interval_index import build_interval_index

    document.interval_index = build_interval_index(hierarchy, len(tokens))
    document.substance_index = build_substance_index(document)
    blob = write_gpm(document, cells=cells, hierarchy=hierarchy)
    separator_perm = scan_perm_code(gaps)

    from gpm.reader import reconstruct_text

    lossless = reconstruct_text(document) == source

    header_bytes = _genome_bytes(header)
    _, _, separator_bytes = read_file_header_fields(blob)
    payload_len = struct.unpack_from("<I", blob, 25)[0]
    body_bytes = payload_len - header_bytes - separator_bytes - _explicit_bytes(explicit)
    source_bytes = len(source.encode("utf-8"))
    file_bytes = len(blob)
    flags = blob[4] if len(blob) > 4 else 0
    body_mode = "cell" if flags & FLAG_BODY_CELL else "flat"

    stats = GpmCompileStats(
        source_bytes=source_bytes,
        file_bytes=file_bytes,
        header_bytes=header_bytes,
        body_bytes=max(0, body_bytes),
        separator_bytes=separator_bytes,
        separator_perm=separator_perm,
        unique_words=len(header),
        total_tokens=len(tokens),
        skipped_tokens=skipped,
        compression_ratio=round(file_bytes / source_bytes, 4) if source_bytes else 0.0,
        lossless=lossless,
        zellen_anzahl=len(cells),
        body_mode=body_mode,
        cell_count_encodable=len(cells) if body_mode == "cell" else 0,
    )
    return document, blob, stats
