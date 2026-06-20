"""
.gpm Binärformat

Version 7 (aktuell) — GAP-RLE + Separator-Absorption + Hierarchie
Version 6 — Zell-Geometrie + orthogonales Gitter (Lesen)
Version 5 — Zell-Geometrie (I_Satz) + v4-Genom/Separator
Version 4 — modellpassende Integer-Stufen 2/4/8/16
Version 3 — kompakter Separator-Layer + Perm-Code (Lesen)
Version 2 — Legacy-Lesen (u32-Gaps)
Version 1 — Legacy-Lesen
"""

from __future__ import annotations

import struct
import zlib
from collections import Counter

from ge_prime.config import MAX_CELL_TOKENS
from ge_prime.multiset_geom import perm_decode, perm_space as multiset_perm_space
from gpm.cell_geom import CellGeometry, build_document_cells, cells_cover_document
from gpm.gap_rle import decode_gap_rle, encode_gap_rle
from gpm.hierarchy_geom import (
    DocumentHierarchy,
    HierarchyNode,
    StructuralTree,
    build_document_hierarchy,
    validate_structural_partition,
)
from gpm.int_codec import (
    decode_fixed_int,
    encode_fixed_int,
    perm_space_size,
    perm_width_bytes,
    perm_width_bytes_for_n,
    substance_width_class,
    width_bytes_for_class,
)
from gpm.model import GpmDocument, GpmHeaderEntry, GpmToken
from gpm.reconstruct_v7 import ensure_lossless_gaps, merge_gaps, derive_gaps, reconstruct_text_v7
from gpm.separator_codec import decode_gaps, encode_gaps, scan_perm_code

MAGIC_PREFIX = b"GPM"
VERSION = 7
VERSION_V6 = 6
VERSION_V5 = 5
VERSION_V4 = 4
VERSION_V3 = 3
VERSION_V2 = 2
LEGACY_VERSION = 1

FLAG_BODY_CELL = 0x01
FLAG_BODY_HIER = 0x02
FLAG_STRUCT = 0x04
FLAG_GAP_RLE = 0x08

FILE_HEADER_SIZE = 29
FILE_HEADER_SIZE_V1 = 18

MAX_HEADER_ENTRIES = 65_535
MAX_BODY_TOKENS = 10_000_000
MAX_EXPLICIT_ENTRIES = MAX_BODY_TOKENS
MAX_STRING_BYTES = 1 << 20
MAX_SUBSTANCE_BYTES = 8192
MAX_SEPARATOR_BYTES = 16 * 1024 * 1024


class GpmFormatError(ValueError):
    """Ungültige oder beschädigte .gpm-Datei."""


def _pack_uint_be(value: int) -> bytes:
    if value < 0:
        raise GpmFormatError("Substanz darf nicht negativ sein.")
    if value == 0:
        return b"\x00"
    length = (value.bit_length() + 7) // 8
    if length > MAX_SUBSTANCE_BYTES:
        raise GpmFormatError("Substanz zu groß für .gpm.")
    return value.to_bytes(length, "big")


def _unpack_uint_be(data: bytes) -> int:
    if not data:
        return 0
    return int.from_bytes(data, "big")


def _encode_utf8(text: str, *, field: str) -> bytes:
    encoded = text.encode("utf-8")
    if len(encoded) > MAX_STRING_BYTES:
        raise GpmFormatError(f"{field} zu lang (>{MAX_STRING_BYTES} Byte).")
    return encoded


def _build_genome_v4(document: GpmDocument) -> bytes:
    genome = bytearray()
    for entry in document.header:
        original = _encode_utf8(entry.word_original, field="Original")
        normalized = _encode_utf8(entry.word_normalized, field="Normalisiert")
        s_class = substance_width_class(entry.substance)
        s_bytes = width_bytes_for_class(s_class)
        genome += struct.pack("<H", len(original)) + original
        genome += struct.pack("<H", len(normalized)) + normalized
        genome += struct.pack("<B", s_class & 0x03)
        try:
            genome += encode_fixed_int(entry.substance, s_bytes)
        except ValueError as exc:
            raise GpmFormatError(str(exc)) from exc
    return bytes(genome)


def _build_body_v4(document: GpmDocument) -> bytes:
    body = bytearray()
    for token in document.tokens:
        if token.word_id >= len(document.header):
            raise GpmFormatError(f"Ungültige Word-ID {token.word_id}.")
        if not 0 <= token.case_code <= 255:
            raise GpmFormatError("Ungültiger Case-Code.")
        entry = document.header[token.word_id]
        n = perm_space_size(entry.word_normalized)
        if not 1 <= token.perm_index <= n:
            raise GpmFormatError(
                f"Index I={token.perm_index} außerhalb des Permutationsraums N={n}."
            )
        i_bytes = perm_width_bytes(entry.word_normalized)
        body += struct.pack("<HB", token.word_id, token.case_code)
        try:
            body += encode_fixed_int(token.perm_index, i_bytes)
        except ValueError as exc:
            raise GpmFormatError(str(exc)) from exc
    return bytes(body)


def _build_explicit(document: GpmDocument) -> bytes:
    explicit = bytearray()
    for token_index, text in document.explicit:
        if not 0 <= token_index < len(document.tokens):
            raise GpmFormatError(f"Explicit-Index {token_index} außerhalb des Body.")
        raw = _encode_utf8(text, field="Explicit")
        explicit += struct.pack("<II", token_index, len(raw)) + raw
    return bytes(explicit)


def _build_body_v5_cell(
    document: GpmDocument,
    cells: list[CellGeometry],
) -> bytes:
    body = bytearray()
    body += struct.pack("<H", len(cells))
    for cell in cells:
        k = len(cell.categories)
        if k > 0xFFFF:
            raise GpmFormatError("Zu viele Kategorien in einer Zelle.")
        total_l = sum(cell.frequencies)
        if total_l > MAX_CELL_TOKENS:
            raise GpmFormatError(
                f"Zell-Länge {total_l} überschreitet MAX_CELL_TOKENS={MAX_CELL_TOKENS}."
            )
        if total_l != cell.token_count:
            raise GpmFormatError("Skelett-Summe passt nicht zur Zelllänge.")
        body += struct.pack("<H", k)
        for freq in cell.frequencies:
            if freq > 0xFFFF:
                raise GpmFormatError("Frequenz zu groß für u16.")
            body += struct.pack("<H", freq)
        i_bytes = perm_width_bytes_for_n(cell.perm_space)
        if not 1 <= cell.perm_index <= cell.perm_space:
            raise GpmFormatError(
                f"I_Satz={cell.perm_index} außerhalb N={cell.perm_space}."
            )
        try:
            body += encode_fixed_int(cell.perm_index, i_bytes)
        except ValueError as exc:
            raise GpmFormatError(str(exc)) from exc
        for cat in cell.categories:
            if cat.word_id >= len(document.header):
                raise GpmFormatError(f"Ungültige Word-ID {cat.word_id}.")
            entry = document.header[cat.word_id]
            n = perm_space_size(entry.word_normalized)
            if not 1 <= cat.perm_index <= n:
                raise GpmFormatError(
                    f"I_Wort={cat.perm_index} außerhalb N={n}."
                )
            w_bytes = perm_width_bytes(entry.word_normalized)
            body += struct.pack("<HB", cat.word_id, cat.case_code)
            try:
                body += encode_fixed_int(cat.perm_index, w_bytes)
            except ValueError as exc:
                raise GpmFormatError(str(exc)) from exc
    return bytes(body)


def _build_structural_index(hierarchy: DocumentHierarchy) -> bytes:
    """Schicht 2 — nur Topologie, keine Wort-IDs (Gesetz 1 write-side)."""
    body = bytearray()
    pages = hierarchy.structural.pages or [
        HierarchyNode(
            layer="structural",
            level="page",
            token_start=0,
            token_count=sum(l.token_count for l in hierarchy.structural.lines),
        )
    ]
    body += struct.pack("<H", len(pages))
    for page in pages:
        page_lines = [
            line
            for line in hierarchy.structural.lines
            if line.token_start >= page.token_start
            and line.token_start + line.token_count <= page.token_start + page.token_count
        ]
        if not page_lines and hierarchy.structural.lines:
            page_lines = hierarchy.structural.lines
        body += struct.pack("<H", len(page_lines))
        for line in page_lines:
            body += struct.pack("<H", line.token_count)
            k_line = len(line.frequencies)
            body += struct.pack("<H", k_line)
            for freq in line.frequencies:
                body += struct.pack("<H", freq)
            n_line = max(line.perm_space, 1)
            i_bytes = min(perm_width_bytes_for_n(n_line), 8)
            if not 1 <= line.perm_index <= max(n_line, 1):
                i_bytes = 1
                i_val = 1
            else:
                i_val = line.perm_index
            body += struct.pack("<B", i_bytes)
            try:
                body += encode_fixed_int(i_val, i_bytes)
            except ValueError:
                body += encode_fixed_int(1, 1)
    return bytes(body)


def _read_structural_index(
    data: bytes,
    offset: int,
    body_end: int,
    token_count: int,
) -> tuple[list[HierarchyNode], int]:
    """Gesetz 1 — kumulativer token_cursor, fail-fast assert."""
    def need(n: int) -> None:
        if offset + n > body_end:
            raise GpmFormatError("Structural index abgeschnitten.")

    need(2)
    (page_count,) = struct.unpack_from("<H", data, offset)
    offset += 2
    token_cursor = 0
    structural_lines: list[HierarchyNode] = []

    for _page_idx in range(page_count):
        need(2)
        (page_line_count,) = struct.unpack_from("<H", data, offset)
        offset += 2
        page_start = token_cursor
        page_lines: list[HierarchyNode] = []
        for _ in range(page_line_count):
            need(2)
            (line_token_count,) = struct.unpack_from("<H", data, offset)
            offset += 2
            if line_token_count > MAX_BODY_TOKENS:
                raise GpmFormatError("Zeilen-Token-Anzahl zu groß.")
            need(2)
            (k_line,) = struct.unpack_from("<H", data, offset)
            offset += 2
            freqs: list[int] = []
            for _k in range(k_line):
                need(2)
                (freq,) = struct.unpack_from("<H", data, offset)
                offset += 2
                freqs.append(freq)
            n_line = (
                multiset_perm_space(Counter({i: freqs[i] for i in range(len(freqs))}))
                if freqs
                else 1
            )
            need(1)
            (i_bytes,) = struct.unpack_from("<B", data, offset)
            offset += 1
            if i_bytes not in (1, 2, 4, 8, 16):
                i_bytes = 1
            need(i_bytes)
            i_zeile = decode_fixed_int(data[offset : offset + i_bytes], i_bytes)
            offset += i_bytes
            node = HierarchyNode(
                layer="structural",
                level="line",
                token_start=token_cursor,
                token_count=line_token_count,
                perm_index=i_zeile,
                perm_space=max(n_line, 1),
                frequencies=freqs,
                skeleton=freqs,
            )
            structural_lines.append(node)
            page_lines.append(node)
            token_cursor += line_token_count

    if token_cursor != token_count:
        raise GpmFormatError(
            f"Structural partition mismatch: {token_cursor} != {token_count}"
        )
    return structural_lines, offset


def _build_sentence_boundaries(hierarchy: DocumentHierarchy) -> bytes:
    sentences = hierarchy.semantic.sentences
    body = bytearray()
    body += struct.pack("<H", len(sentences))
    for sentence in sentences:
        suffix = getattr(sentence, "boundary_suffix", 0) & 0x03
        body += struct.pack(
            "<IHB",
            sentence.token_start,
            sentence.token_count,
            suffix,
        )
    return bytes(body)


def _read_sentence_boundaries(
    data: bytes,
    offset: int,
    body_end: int,
) -> tuple[list[tuple[int, int, int]], int]:
    if offset + 4 > body_end:
        raise GpmFormatError("Sentence-Boundary-Block fehlt.")
    (block_len,) = struct.unpack_from("<I", data, offset)
    offset += 4
    block_end = offset + block_len
    if block_end > body_end:
        raise GpmFormatError("Sentence-Boundary-Block abgeschnitten.")
    if block_len == 0:
        return [], block_end
    if offset + 2 > block_end:
        raise GpmFormatError("Sentence-Boundary-Header fehlt.")
    (count,) = struct.unpack_from("<H", data, offset)
    offset += 2
    entries: list[tuple[int, int, int]] = []
    for _ in range(count):
        if offset + 7 > block_end:
            raise GpmFormatError("Sentence-Boundary-Eintrag abgeschnitten.")
        token_start, token_count, suffix = struct.unpack_from("<IHB", data, offset)
        offset += 7
        entries.append((token_start, token_count, suffix & 0x03))
    if offset != block_end:
        raise GpmFormatError("Sentence-Boundary-Block enthält überhängende Bytes.")
    return entries, block_end


def _apply_sentence_boundaries(
    hierarchy: DocumentHierarchy,
    entries: list[tuple[int, int, int]],
) -> None:
    lookup = {(start, count): suffix for start, count, suffix in entries}
    for sentence in hierarchy.semantic.sentences:
        key = (sentence.token_start, sentence.token_count)
        if key in lookup:
            sentence.boundary_suffix = lookup[key]


def _build_body_v7(
    document: GpmDocument,
    hierarchy: DocumentHierarchy,
) -> bytes:
    base = _build_body_v6(document, hierarchy)
    sent_block = _build_sentence_boundaries(hierarchy)
    return base + struct.pack("<I", len(sent_block)) + sent_block


def _attach_document_indices(document: GpmDocument) -> GpmDocument:
    """Hängt IntervalIndex und SubstanceIndex an (v40, auch nach v6-Lesen)."""
    from ge_prime.substance_index import build_substance_index
    from gpm.interval_index import build_interval_index

    hierarchy = document.hierarchy
    if hierarchy is None:
        return document
    return GpmDocument(
        header=document.header,
        tokens=document.tokens,
        gaps=document.gaps,
        explicit=document.explicit,
        cells=document.cells,
        hierarchy=hierarchy,
        interval_index=build_interval_index(hierarchy, len(document.tokens)),
        substance_index=build_substance_index(document),
        gap_rle=document.gap_rle,
    )

def _build_body_v6(
    document: GpmDocument,
    hierarchy: DocumentHierarchy,
) -> bytes:
    cells = build_document_cells(document)
    if not cells_cover_document(document, cells):
        raise GpmFormatError("Zell-Body deckt Dokument nicht ab.")
    try:
        validate_structural_partition(
            len(document.tokens),
            hierarchy.structural.lines,
        )
    except ValueError as exc:
        raise GpmFormatError(str(exc)) from exc
    semantic = _build_body_v5_cell(document, cells)
    structural = _build_structural_index(hierarchy)
    return semantic + struct.pack("<I", len(structural)) + structural


def _read_body_v5_cell(
    data: bytes,
    offset: int,
    body_end: int,
    header: list[GpmHeaderEntry],
) -> tuple[list[GpmToken], int]:
    def need(n: int) -> None:
        if offset + n > body_end:
            raise GpmFormatError("Datei unerwartet zu Ende.")

    need(2)
    (zellen_anzahl,) = struct.unpack_from("<H", data, offset)
    offset += 2
    if zellen_anzahl > MAX_BODY_TOKENS:
        raise GpmFormatError("Zu viele Zellen im Body.")

    tokens: list[GpmToken] = []
    for _ in range(zellen_anzahl):
        need(2)
        (k,) = struct.unpack_from("<H", data, offset)
        offset += 2
        frequencies: list[int] = []
        for _ in range(k):
            need(2)
            (freq,) = struct.unpack_from("<H", data, offset)
            offset += 2
            frequencies.append(freq)
        total_l = sum(frequencies)
        if total_l > MAX_CELL_TOKENS:
            raise GpmFormatError(
                f"Zell-Länge {total_l} überschreitet MAX_CELL_TOKENS={MAX_CELL_TOKENS}."
            )
        if total_l == 0 and k > 0:
            raise GpmFormatError("Leere Zelle mit Kategorien.")
        n_satz = multiset_perm_space(Counter({i: frequencies[i] for i in range(k)}))
        i_bytes = perm_width_bytes_for_n(n_satz)
        need(i_bytes)
        try:
            i_satz = decode_fixed_int(data[offset : offset + i_bytes], i_bytes)
        except ValueError as exc:
            raise GpmFormatError(str(exc)) from exc
        offset += i_bytes
        if not 1 <= i_satz <= n_satz:
            raise GpmFormatError(f"I_Satz={i_satz} außerhalb N={n_satz}.")

        categories: list[tuple[int, int, int]] = []
        for _ in range(k):
            need(3)
            word_id, case_code = struct.unpack_from("<HB", data, offset)
            offset += 3
            if word_id >= len(header):
                raise GpmFormatError(f"Body verweist auf unbekannte Word-ID {word_id}.")
            entry = header[word_id]
            w_bytes = perm_width_bytes(entry.word_normalized)
            need(w_bytes)
            try:
                perm_index = decode_fixed_int(data[offset : offset + w_bytes], w_bytes)
            except ValueError as exc:
                raise GpmFormatError(str(exc)) from exc
            offset += w_bytes
            n_word = perm_space_size(entry.word_normalized)
            if not 1 <= perm_index <= n_word:
                raise GpmFormatError(
                    f"I_Wort={perm_index} außerhalb N={n_word}."
                )
            categories.append((word_id, case_code, perm_index))

        counts = Counter({i: frequencies[i] for i in range(k)})
        path = perm_decode(counts, i_satz)
        if len(path) != total_l:
            raise GpmFormatError("Entrollter Zell-Pfad passt nicht zur Länge.")
        for cat_id in path:
            word_id, case_code, perm_index = categories[cat_id]
            tokens.append(
                GpmToken(
                    word_id=word_id,
                    perm_index=perm_index,
                    case_code=case_code,
                )
            )

    return tokens, offset


def write_gpm(
    document: GpmDocument,
    *,
    cells: list[CellGeometry] | None = None,
    hierarchy: DocumentHierarchy | None = None,
    version: int | None = None,
) -> bytes:
    """Schreibt .gpm (Standard: v7 mit GAP-RLE, optional v6/v5/v4)."""
    target_version = VERSION if version is None else version
    if target_version not in (VERSION, VERSION_V6, VERSION_V5, VERSION_V4):
        raise GpmFormatError(f"Schreiben für Version {target_version} nicht unterstützt.")

    if len(document.header) > MAX_HEADER_ENTRIES:
        raise GpmFormatError("Zu viele Wörter im Header.")
    if len(document.tokens) > MAX_BODY_TOKENS:
        raise GpmFormatError("Zu viele Token im Body.")

    expected_gaps = len(document.tokens) + 1
    if len(document.gaps) != expected_gaps:
        raise GpmFormatError(
            f"Gap-Anzahl {len(document.gaps)} ≠ erwartet {expected_gaps}."
        )

    genome = _build_genome_v4(document)
    explicit = _build_explicit(document)
    flags = 0
    middle_blob = b""
    perm = 0

    if target_version == VERSION:
        if cells is None:
            cells = build_document_cells(document)
        if hierarchy is None:
            hierarchy = build_document_hierarchy(document)
        gap_rle = ensure_lossless_gaps(document.gaps, hierarchy)
        draft = GpmDocument(
            header=document.header,
            tokens=document.tokens,
            gaps=document.gaps,
            explicit=document.explicit,
            hierarchy=hierarchy,
            gap_rle=gap_rle,
        )
        virtual = reconstruct_text_v7(draft)
        from gpm.reconstruct_v7 import _reconstruct_from_gaps

        original = _reconstruct_from_gaps(document, document.gaps)
        if virtual != original:
            raise GpmFormatError("V7 serialization loss detected!")
        middle_blob = encode_gap_rle(gap_rle)
        body = _build_body_v7(document, hierarchy)
        flags = FLAG_BODY_CELL | FLAG_BODY_HIER | FLAG_STRUCT | FLAG_GAP_RLE
    elif target_version in (VERSION_V6, VERSION_V5):
        perm = scan_perm_code(document.gaps)
        middle_blob = encode_gaps(document.gaps, perm)
        if len(middle_blob) > MAX_SEPARATOR_BYTES:
            raise GpmFormatError("Separator-Schicht zu groß.")
        if cells is None:
            cells = build_document_cells(document)
        if hierarchy is None and target_version == VERSION_V6:
            hierarchy = build_document_hierarchy(document)
        use_cell = bool(cells) and cells_cover_document(document, cells)
        if target_version == VERSION_V6 and hierarchy is not None:
            body = _build_body_v6(document, hierarchy)
            flags = FLAG_BODY_CELL | FLAG_BODY_HIER | FLAG_STRUCT
        elif use_cell:
            try:
                body = _build_body_v5_cell(document, cells)
                flags = FLAG_BODY_CELL
            except GpmFormatError:
                use_cell = False
        if flags == 0:
            body = _build_body_v4(document)
            flags = 0
    else:
        perm = scan_perm_code(document.gaps)
        middle_blob = encode_gaps(document.gaps, perm)
        if len(middle_blob) > MAX_SEPARATOR_BYTES:
            raise GpmFormatError("Separator-Schicht zu groß.")
        body = _build_body_v4(document)

    payload = genome + body + middle_blob + explicit

    file_header = MAGIC_PREFIX + struct.pack(
        "<BBIIIIII",
        target_version,
        flags,
        len(document.header),
        len(document.tokens),
        perm,
        len(document.explicit),
        len(middle_blob),
        len(payload),
    )

    blob = file_header + payload
    crc = zlib.crc32(blob) & 0xFFFFFFFF
    return blob + struct.pack("<I", crc)


def _detect_version(data: bytes) -> int:
    if len(data) < 5 or data[:3] != MAGIC_PREFIX:
        raise GpmFormatError("Keine gültige .gpm-Datei (Magic fehlt).")
    return data[3]


def read_file_header_fields(data: bytes) -> tuple[int, int, int]:
    """Liest (version, field_a, middle_len) — v7: gap_rle_len; v≤6: separator."""
    if len(data) < 4 or data[:3] != MAGIC_PREFIX:
        return 0, 0, 0
    version = data[3]
    if version in (VERSION, VERSION_V6, VERSION_V5, VERSION_V4, VERSION_V3, VERSION_V2) and len(data) >= FILE_HEADER_SIZE:
        field_a = struct.unpack_from("<I", data, 13)[0]
        middle_len = struct.unpack_from("<I", data, 21)[0]
        return version, field_a, middle_len
    return version, 0, 0


def read_gpm(data: bytes) -> GpmDocument:
    version = _detect_version(data)
    if version == VERSION:
        return _read_v7(data)
    if version == VERSION_V6:
        return _read_v6(data)
    if version == VERSION_V5:
        return _read_v5(data)
    if version == VERSION_V4:
        return _read_v4(data)
    if version == VERSION_V3:
        return _read_v3(data)
    if version == VERSION_V2:
        return _read_v2(data)
    if version == LEGACY_VERSION:
        return _read_v1(data)
    raise GpmFormatError(f"Nicht unterstützte Version: {version}.")


def _read_header_payload(data: bytes) -> tuple[int, int, int, int, int, int, int]:
    if len(data) < FILE_HEADER_SIZE + 4:
        raise GpmFormatError("Datei zu kurz.")

    stored_crc = struct.unpack_from("<I", data, len(data) - 4)[0]
    actual_crc = zlib.crc32(data[: len(data) - 4]) & 0xFFFFFFFF
    if stored_crc != actual_crc:
        raise GpmFormatError("CRC-Prüfsumme stimmt nicht — Datei beschädigt.")

    (
        version,
        _flags,
        header_count,
        body_count,
        field_a,
        explicit_count,
        field_b,
        payload_len,
    ) = struct.unpack_from("<BBIIIIII", data, 3)

    body_end = len(data) - 4
    expected_payload = body_end - FILE_HEADER_SIZE
    if payload_len != expected_payload:
        raise GpmFormatError("Payload-Länge inkonsistent.")

    return version, header_count, body_count, field_a, explicit_count, field_b, body_end


def _read_genome_body(
    data: bytes,
    offset: int,
    body_end: int,
    header_count: int,
    body_count: int,
) -> tuple[list[GpmHeaderEntry], list[GpmToken], int]:
    def need(n: int) -> None:
        if offset + n > body_end:
            raise GpmFormatError("Datei unerwartet zu Ende.")

    header: list[GpmHeaderEntry] = []
    for word_id in range(header_count):
        need(2)
        (orig_len,) = struct.unpack_from("<H", data, offset)
        offset += 2
        need(orig_len)
        original = data[offset : offset + orig_len].decode("utf-8")
        offset += orig_len

        need(2)
        (norm_len,) = struct.unpack_from("<H", data, offset)
        offset += 2
        need(norm_len)
        normalized = data[offset : offset + norm_len].decode("utf-8")
        offset += norm_len

        need(2)
        (sub_len,) = struct.unpack_from("<H", data, offset)
        offset += 2
        if sub_len > MAX_SUBSTANCE_BYTES:
            raise GpmFormatError("Substanz-Block zu groß.")
        need(sub_len)
        substance = _unpack_uint_be(data[offset : offset + sub_len])
        offset += sub_len

        header.append(
            GpmHeaderEntry(
                word_id=word_id,
                word_original=original,
                word_normalized=normalized,
                substance=substance,
            )
        )

    tokens: list[GpmToken] = []
    for _ in range(body_count):
        need(7)
        word_id, perm_index, case_code = struct.unpack_from("<HIB", data, offset)
        offset += 7
        if word_id >= len(header):
            raise GpmFormatError(f"Body verweist auf unbekannte Word-ID {word_id}.")
        tokens.append(
            GpmToken(word_id=word_id, perm_index=perm_index, case_code=case_code)
        )

    return header, tokens, offset


def _read_explicit(
    data: bytes,
    offset: int,
    body_end: int,
    explicit_count: int,
    tokens: list[GpmToken],
) -> tuple[list[tuple[int, str]], int]:
    explicit: list[tuple[int, str]] = []

    def need(n: int) -> None:
        if offset + n > body_end:
            raise GpmFormatError("Datei unerwartet zu Ende.")

    for _ in range(explicit_count):
        need(8)
        token_index, text_len = struct.unpack_from("<II", data, offset)
        offset += 8
        if token_index >= len(tokens):
            raise GpmFormatError("Explicit-Index außerhalb des Body.")
        if text_len > MAX_STRING_BYTES:
            raise GpmFormatError("Explicit-Block zu groß.")
        need(text_len)
        explicit.append((token_index, data[offset : offset + text_len].decode("utf-8")))
        offset += text_len

    return explicit, offset


def _read_genome_v4(
    data: bytes,
    offset: int,
    body_end: int,
    header_count: int,
) -> tuple[list[GpmHeaderEntry], int]:
    def need(n: int) -> None:
        if offset + n > body_end:
            raise GpmFormatError("Datei unerwartet zu Ende.")

    header: list[GpmHeaderEntry] = []
    for word_id in range(header_count):
        need(2)
        (orig_len,) = struct.unpack_from("<H", data, offset)
        offset += 2
        need(orig_len)
        original = data[offset : offset + orig_len].decode("utf-8")
        offset += orig_len

        need(2)
        (norm_len,) = struct.unpack_from("<H", data, offset)
        offset += 2
        need(norm_len)
        normalized = data[offset : offset + norm_len].decode("utf-8")
        offset += norm_len

        need(1)
        (flags,) = struct.unpack_from("<B", data, offset)
        offset += 1
        s_class = flags & 0x03
        s_bytes = width_bytes_for_class(s_class)
        need(s_bytes)
        try:
            substance = decode_fixed_int(data[offset : offset + s_bytes], s_bytes)
        except ValueError as exc:
            raise GpmFormatError(str(exc)) from exc
        offset += s_bytes

        header.append(
            GpmHeaderEntry(
                word_id=word_id,
                word_original=original,
                word_normalized=normalized,
                substance=substance,
                s_width_class=s_class,
            )
        )

    return header, offset


def _read_tokens_v4(
    data: bytes,
    offset: int,
    body_end: int,
    header: list[GpmHeaderEntry],
    body_count: int,
) -> tuple[list[GpmToken], int]:
    def need(n: int) -> None:
        if offset + n > body_end:
            raise GpmFormatError("Datei unerwartet zu Ende.")

    tokens: list[GpmToken] = []
    for _ in range(body_count):
        need(3)
        word_id, case_code = struct.unpack_from("<HB", data, offset)
        offset += 3
        if word_id >= len(header):
            raise GpmFormatError(f"Body verweist auf unbekannte Word-ID {word_id}.")
        entry = header[word_id]
        i_bytes = perm_width_bytes(entry.word_normalized)
        need(i_bytes)
        try:
            perm_index = decode_fixed_int(data[offset : offset + i_bytes], i_bytes)
        except ValueError as exc:
            raise GpmFormatError(str(exc)) from exc
        offset += i_bytes
        n = perm_space_size(entry.word_normalized)
        if not 1 <= perm_index <= n:
            raise GpmFormatError(
                f"Index I={perm_index} außerhalb des Permutationsraums N={n}."
            )
        tokens.append(
            GpmToken(word_id=word_id, perm_index=perm_index, case_code=case_code)
        )

    return tokens, offset


def _read_v5(data: bytes) -> GpmDocument:
    (
        version,
        header_count,
        body_count,
        separator_perm,
        explicit_count,
        separator_len,
        body_end,
    ) = _read_header_payload(data)

    if version != VERSION_V5:
        raise GpmFormatError(f"Versionskonflikt: {version}.")
    if header_count > MAX_HEADER_ENTRIES:
        raise GpmFormatError("Zu viele Genom-Einträge.")
    if body_count > MAX_BODY_TOKENS:
        raise GpmFormatError("Zu viele Body-Token.")
    if explicit_count > MAX_EXPLICIT_ENTRIES:
        raise GpmFormatError("Zu viele Explicit-Einträge.")
    if separator_len > MAX_SEPARATOR_BYTES:
        raise GpmFormatError("Separator-Block zu groß.")

    flags = struct.unpack_from("<B", data, 4)[0]
    offset = FILE_HEADER_SIZE
    header, offset = _read_genome_v4(data, offset, body_end, header_count)

    if flags & FLAG_BODY_CELL:
        tokens, offset = _read_body_v5_cell(data, offset, body_end, header)
    else:
        tokens, offset = _read_tokens_v4(
            data, offset, body_end, header, body_count
        )

    if len(tokens) != body_count:
        raise GpmFormatError(
            f"Token-Anzahl {len(tokens)} ≠ Header body_count {body_count}."
        )

    if offset + separator_len > body_end:
        raise GpmFormatError("Separator-Block abgeschnitten.")
    separator_blob = data[offset : offset + separator_len]
    offset += separator_len

    gap_count = body_count + 1
    try:
        gaps = decode_gaps(separator_blob, separator_perm, gap_count)
    except ValueError as exc:
        raise GpmFormatError(str(exc)) from exc

    explicit, offset = _read_explicit(
        data, offset, body_end, explicit_count, tokens
    )

    if offset != body_end:
        raise GpmFormatError("Überhängende Bytes im Payload.")

    return GpmDocument(header=header, tokens=tokens, gaps=gaps, explicit=explicit)


def _read_v7(data: bytes) -> GpmDocument:
    (
        version,
        header_count,
        body_count,
        _reserved,
        explicit_count,
        gap_rle_len,
        body_end,
    ) = _read_header_payload(data)

    if version != VERSION:
        raise GpmFormatError(f"Versionskonflikt: {version}.")
    if header_count > MAX_HEADER_ENTRIES:
        raise GpmFormatError("Zu viele Genom-Einträge.")
    if body_count > MAX_BODY_TOKENS:
        raise GpmFormatError("Zu viele Body-Token.")
    if explicit_count > MAX_EXPLICIT_ENTRIES:
        raise GpmFormatError("Zu viele Explicit-Einträge.")
    if gap_rle_len > MAX_SEPARATOR_BYTES:
        raise GpmFormatError("GAP-RLE-Block zu groß.")

    flags = struct.unpack_from("<B", data, 4)[0]
    offset = FILE_HEADER_SIZE
    header, offset = _read_genome_v4(data, offset, body_end, header_count)

    structural_lines: list[HierarchyNode] = []
    sentence_entries: list[tuple[int, int, int]] = []
    if flags & FLAG_BODY_CELL:
        tokens, offset = _read_body_v5_cell(data, offset, body_end, header)
    else:
        tokens, offset = _read_tokens_v4(
            data, offset, body_end, header, body_count
        )

    if len(tokens) != body_count:
        raise GpmFormatError(
            f"Token-Anzahl {len(tokens)} ≠ Header body_count {body_count}."
        )

    if flags & FLAG_STRUCT:
        if offset + 4 > body_end:
            raise GpmFormatError("Structural index fehlt.")
        (struct_len,) = struct.unpack_from("<I", data, offset)
        offset += 4
        struct_end = offset + struct_len
        if struct_end > body_end:
            raise GpmFormatError("Structural index abgeschnitten.")
        structural_lines, offset = _read_structural_index(
            data, offset, struct_end, body_count
        )
        if offset != struct_end:
            raise GpmFormatError("Structural index enthält überhängende Bytes.")

    if flags & FLAG_BODY_HIER:
        sentence_entries, offset = _read_sentence_boundaries(data, offset, body_end)

    if offset + gap_rle_len > body_end:
        raise GpmFormatError("GAP-RLE-Block abgeschnitten.")
    gap_rle_blob = data[offset : offset + gap_rle_len]
    offset += gap_rle_len
    try:
        gap_rle = decode_gap_rle(gap_rle_blob)
    except ValueError as exc:
        raise GpmFormatError(str(exc)) from exc

    explicit, offset = _read_explicit(
        data, offset, body_end, explicit_count, tokens
    )

    if offset != body_end:
        raise GpmFormatError("Überhängende Bytes im Payload.")

    draft = GpmDocument(
        header=header,
        tokens=tokens,
        gaps=[" "] * (body_count + 1),
        explicit=explicit,
    )
    built = build_document_hierarchy(draft)
    hierarchy: DocumentHierarchy | None = None
    if flags & FLAG_STRUCT and structural_lines:
        try:
            validate_structural_partition(body_count, structural_lines)
        except ValueError as exc:
            raise GpmFormatError(str(exc)) from exc
        hierarchy = DocumentHierarchy(
            semantic=built.semantic,
            structural=StructuralTree(lines=structural_lines, pages=built.structural.pages),
        )
    else:
        hierarchy = built

    if sentence_entries:
        _apply_sentence_boundaries(hierarchy, sentence_entries)

    derived = derive_gaps(body_count, hierarchy, sentence_entries=sentence_entries or None)
    gaps = merge_gaps(derived, gap_rle)
    final_draft = GpmDocument(
        header=header, tokens=tokens, gaps=gaps, explicit=explicit
    )
    hierarchy = build_document_hierarchy(final_draft)
    if flags & FLAG_STRUCT and structural_lines:
        hierarchy = DocumentHierarchy(
            semantic=hierarchy.semantic,
            structural=StructuralTree(
                lines=structural_lines, pages=hierarchy.structural.pages
            ),
        )
    if sentence_entries:
        _apply_sentence_boundaries(hierarchy, sentence_entries)

    document = GpmDocument(
        header=header,
        tokens=tokens,
        gaps=gaps,
        explicit=explicit,
        hierarchy=hierarchy,
        gap_rle=gap_rle,
    )
    return _attach_document_indices(document)


def _read_v6(data: bytes) -> GpmDocument:
    (
        version,
        header_count,
        body_count,
        separator_perm,
        explicit_count,
        separator_len,
        body_end,
    ) = _read_header_payload(data)

    if version != VERSION_V6:
        raise GpmFormatError(f"Versionskonflikt: {version}.")
    if header_count > MAX_HEADER_ENTRIES:
        raise GpmFormatError("Zu viele Genom-Einträge.")
    if body_count > MAX_BODY_TOKENS:
        raise GpmFormatError("Zu viele Body-Token.")
    if explicit_count > MAX_EXPLICIT_ENTRIES:
        raise GpmFormatError("Zu viele Explicit-Einträge.")
    if separator_len > MAX_SEPARATOR_BYTES:
        raise GpmFormatError("Separator-Block zu groß.")

    flags = struct.unpack_from("<B", data, 4)[0]
    offset = FILE_HEADER_SIZE
    header, offset = _read_genome_v4(data, offset, body_end, header_count)

    structural_lines: list[HierarchyNode] = []
    if flags & FLAG_BODY_CELL:
        tokens, offset = _read_body_v5_cell(data, offset, body_end, header)
    else:
        tokens, offset = _read_tokens_v4(
            data, offset, body_end, header, body_count
        )

    if len(tokens) != body_count:
        raise GpmFormatError(
            f"Token-Anzahl {len(tokens)} ≠ Header body_count {body_count}."
        )

    if flags & FLAG_STRUCT:
        if offset + 4 > body_end:
            raise GpmFormatError("Structural index fehlt.")
        (struct_len,) = struct.unpack_from("<I", data, offset)
        offset += 4
        struct_end = offset + struct_len
        if struct_end > body_end:
            raise GpmFormatError("Structural index abgeschnitten.")
        structural_lines, offset = _read_structural_index(
            data, offset, struct_end, body_count
        )
        if offset != struct_end:
            raise GpmFormatError("Structural index enthält überhängende Bytes.")

    if offset + separator_len > body_end:
        raise GpmFormatError("Separator-Block abgeschnitten.")
    separator_blob = data[offset : offset + separator_len]
    offset += separator_len

    gap_count = body_count + 1
    try:
        gaps = decode_gaps(separator_blob, separator_perm, gap_count)
    except ValueError as exc:
        raise GpmFormatError(str(exc)) from exc

    explicit, offset = _read_explicit(
        data, offset, body_end, explicit_count, tokens
    )

    if offset != body_end:
        raise GpmFormatError("Überhängende Bytes im Payload.")

    draft = GpmDocument(header=header, tokens=tokens, gaps=gaps, explicit=explicit)
    hierarchy: DocumentHierarchy | None = None
    if flags & FLAG_STRUCT and structural_lines:
        built = build_document_hierarchy(draft)
        try:
            validate_structural_partition(body_count, structural_lines)
        except ValueError as exc:
            raise GpmFormatError(str(exc)) from exc
        hierarchy = DocumentHierarchy(
            semantic=built.semantic,
            structural=StructuralTree(lines=structural_lines, pages=built.structural.pages),
        )

    document = GpmDocument(
        header=header,
        tokens=tokens,
        gaps=gaps,
        explicit=explicit,
        hierarchy=hierarchy,
    )
    if hierarchy is not None:
        return _attach_document_indices(document)
    return document


def _read_v4(data: bytes) -> GpmDocument:
    (
        version,
        header_count,
        body_count,
        separator_perm,
        explicit_count,
        separator_len,
        body_end,
    ) = _read_header_payload(data)

    if version != VERSION_V4:
        raise GpmFormatError(f"Versionskonflikt: {version}.")
    if header_count > MAX_HEADER_ENTRIES:
        raise GpmFormatError("Zu viele Genom-Einträge.")
    if body_count > MAX_BODY_TOKENS:
        raise GpmFormatError("Zu viele Body-Token.")
    if explicit_count > MAX_EXPLICIT_ENTRIES:
        raise GpmFormatError("Zu viele Explicit-Einträge.")
    if separator_len > MAX_SEPARATOR_BYTES:
        raise GpmFormatError("Separator-Block zu groß.")

    offset = FILE_HEADER_SIZE
    header, offset = _read_genome_v4(data, offset, body_end, header_count)
    tokens, offset = _read_tokens_v4(
        data, offset, body_end, header, body_count
    )

    if offset + separator_len > body_end:
        raise GpmFormatError("Separator-Block abgeschnitten.")
    separator_blob = data[offset : offset + separator_len]
    offset += separator_len

    gap_count = body_count + 1
    try:
        gaps = decode_gaps(separator_blob, separator_perm, gap_count)
    except ValueError as exc:
        raise GpmFormatError(str(exc)) from exc

    explicit, offset = _read_explicit(
        data, offset, body_end, explicit_count, tokens
    )

    if offset != body_end:
        raise GpmFormatError("Überhängende Bytes im Payload.")

    return GpmDocument(header=header, tokens=tokens, gaps=gaps, explicit=explicit)


def _read_v3(data: bytes) -> GpmDocument:
    (
        version,
        header_count,
        body_count,
        separator_perm,
        explicit_count,
        separator_len,
        body_end,
    ) = _read_header_payload(data)

    if version != VERSION_V3:
        raise GpmFormatError(f"Versionskonflikt: {version}.")
    if header_count > MAX_HEADER_ENTRIES:
        raise GpmFormatError("Zu viele Genom-Einträge.")
    if body_count > MAX_BODY_TOKENS:
        raise GpmFormatError("Zu viele Body-Token.")
    if explicit_count > MAX_EXPLICIT_ENTRIES:
        raise GpmFormatError("Zu viele Explicit-Einträge.")
    if separator_len > MAX_SEPARATOR_BYTES:
        raise GpmFormatError("Separator-Block zu groß.")

    offset = FILE_HEADER_SIZE
    header, tokens, offset = _read_genome_body(
        data, offset, body_end, header_count, body_count
    )

    if offset + separator_len > body_end:
        raise GpmFormatError("Separator-Block abgeschnitten.")
    separator_blob = data[offset : offset + separator_len]
    offset += separator_len

    gap_count = body_count + 1
    try:
        gaps = decode_gaps(separator_blob, separator_perm, gap_count)
    except ValueError as exc:
        raise GpmFormatError(str(exc)) from exc

    explicit, offset = _read_explicit(
        data, offset, body_end, explicit_count, tokens
    )

    if offset != body_end:
        raise GpmFormatError("Überhängende Bytes im Payload.")

    return GpmDocument(header=header, tokens=tokens, gaps=gaps, explicit=explicit)


def _read_v2(data: bytes) -> GpmDocument:
    (
        version,
        header_count,
        body_count,
        gap_count,
        explicit_count,
        _reserved,
        body_end,
    ) = _read_header_payload(data)

    if version != VERSION_V2:
        raise GpmFormatError(f"Versionskonflikt: {version}.")
    if header_count > MAX_HEADER_ENTRIES:
        raise GpmFormatError("Zu viele Genom-Einträge.")
    if body_count > MAX_BODY_TOKENS:
        raise GpmFormatError("Zu viele Body-Token.")
    if gap_count != body_count + 1:
        raise GpmFormatError("Gap-Anzahl inkonsistent.")
    if explicit_count > MAX_EXPLICIT_ENTRIES:
        raise GpmFormatError("Zu viele Explicit-Einträge.")

    offset = FILE_HEADER_SIZE
    header, tokens, offset = _read_genome_body(
        data, offset, body_end, header_count, body_count
    )

    gaps: list[str] = []
    for _ in range(gap_count):
        if offset + 4 > body_end:
            raise GpmFormatError("Datei unerwartet zu Ende.")
        (gap_len,) = struct.unpack_from("<I", data, offset)
        offset += 4
        if gap_len > MAX_STRING_BYTES:
            raise GpmFormatError("Gap-Block zu groß.")
        if offset + gap_len > body_end:
            raise GpmFormatError("Gap-Block abgeschnitten.")
        gaps.append(data[offset : offset + gap_len].decode("utf-8"))
        offset += gap_len

    explicit, offset = _read_explicit(
        data, offset, body_end, explicit_count, tokens
    )

    if offset != body_end:
        raise GpmFormatError("Überhängende Bytes im Payload.")

    return GpmDocument(header=header, tokens=tokens, gaps=gaps, explicit=explicit)


def _read_v1(data: bytes) -> GpmDocument:
    """Legacy v1 → Modell (Wörter durch Leerzeichen getrennt)."""
    if len(data) < FILE_HEADER_SIZE_V1:
        raise GpmFormatError("Datei zu kurz.")

    version, _flags, header_count, body_count, _reserved = struct.unpack_from(
        "<BBIII", data, 4
    )
    if version != LEGACY_VERSION:
        raise GpmFormatError(f"Versionskonflikt (v1): {version}.")

    offset = FILE_HEADER_SIZE_V1
    header: list[GpmHeaderEntry] = []

    for word_id in range(header_count):
        if offset + 2 > len(data):
            raise GpmFormatError("Header abgeschnitten.")
        (orig_len,) = struct.unpack_from("<H", data, offset)
        offset += 2
        original = data[offset : offset + orig_len].decode("utf-8")
        offset += orig_len

        (norm_len,) = struct.unpack_from("<H", data, offset)
        offset += 2
        normalized = data[offset : offset + norm_len].decode("utf-8")
        offset += norm_len

        (sub_len,) = struct.unpack_from("<H", data, offset)
        offset += 2
        if sub_len > MAX_SUBSTANCE_BYTES:
            raise GpmFormatError("Substanz-Block zu groß.")
        substance = _unpack_uint_be(data[offset : offset + sub_len])
        offset += sub_len

        header.append(
            GpmHeaderEntry(
                word_id=word_id,
                word_original=original,
                word_normalized=normalized,
                substance=substance,
            )
        )

    tokens: list[GpmToken] = []
    explicit: list[tuple[int, str]] = []
    for idx in range(body_count):
        if offset + 6 > len(data):
            raise GpmFormatError("Body abgeschnitten.")
        word_id, perm_index = struct.unpack_from("<HI", data, offset)
        offset += 6
        if word_id >= len(header):
            raise GpmFormatError(f"Body verweist auf unbekannte Word-ID {word_id}.")
        tokens.append(GpmToken(word_id=word_id, perm_index=perm_index, case_code=3))
        explicit.append((idx, header[word_id].word_original))

    if offset != len(data):
        raise GpmFormatError("Überhängende Bytes am Dateiende.")

    gaps = [""] + [" "] * max(0, body_count - 1) + ([""] if body_count else [])
    if body_count == 0:
        gaps = [""]

    return GpmDocument(header=header, tokens=tokens, gaps=gaps, explicit=explicit)
