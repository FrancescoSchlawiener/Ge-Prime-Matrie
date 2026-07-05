"""
.gpm Binärformat für GPM/functions.

Version 8 (Standard) — v4-Layout + AlphabetProfile + optional GAP-RLE-Vollspeicher
Version 4 — OG-kompatibel (Lesen), flaches Token-Body + Separator-Layer
"""

from __future__ import annotations

import struct
import zlib

from alphabets import AlphabetProfile
from analysis.binary.gap_rle import decode_full_gaps, encode_full_gaps
from analysis.binary.int_codec import (
    decode_fixed_int,
    encode_fixed_int,
    perm_space_size,
    perm_width_bytes,
    substance_width_class,
    width_bytes_for_class,
)
from analysis.binary.separator_codec import decode_gaps, encode_gaps, scan_perm_code
from analysis.case.policy import DEFAULT_CASE_POLICY
from analysis.document.invariants import assert_gap_symmetry
from analysis.document.model import GpmDocument, GpmHeaderEntry, GpmToken
from gpm_types.classify import PayloadKind

MAGIC_PREFIX = b"GPM"
VERSION_V4 = 4
VERSION_V8 = 8
VERSION = 9

FLAG_BODY_CELL = 0x01
FLAG_BODY_HIER = 0x02
FLAG_STRUCT = 0x04
FLAG_GAP_RLE = 0x08
FLAG_PROFILE = 0x10
FLAG_FRACTAL = 0x20

FILE_HEADER_SIZE = 29

MAX_HEADER_ENTRIES = 65_535
MAX_BODY_TOKENS = 10_000_000
MAX_EXPLICIT_ENTRIES = MAX_BODY_TOKENS
MAX_STRING_BYTES = 1 << 20
MAX_MIDDLE_BYTES = 16 * 1024 * 1024


class GpmFormatError(ValueError):
    """Ungültige oder beschädigte .gpm-Datei."""


def _encode_utf8(text: str, *, field: str) -> bytes:
    encoded = text.encode("utf-8")
    if len(encoded) > MAX_STRING_BYTES:
        raise GpmFormatError(f"{field} zu lang (>{MAX_STRING_BYTES} Byte).")
    return encoded


def _profile_to_bytes(profile: AlphabetProfile) -> bytes:
    name = profile.value if isinstance(profile, AlphabetProfile) else str(profile)
    raw = _encode_utf8(name, field="Profil")
    if len(raw) > 255:
        raise GpmFormatError("Profilname zu lang.")
    return struct.pack("<B", len(raw)) + raw


def _profile_from_bytes(data: bytes, offset: int) -> tuple[AlphabetProfile, int]:
    if offset >= len(data):
        raise GpmFormatError("Profil-Block fehlt.")
    (name_len,) = struct.unpack_from("<B", data, offset)
    offset += 1
    if offset + name_len > len(data):
        raise GpmFormatError("Profil-Block abgeschnitten.")
    name = data[offset : offset + name_len].decode("utf-8")
    offset += name_len
    try:
        return AlphabetProfile(name), offset
    except ValueError as exc:
        raise GpmFormatError(f"Unbekanntes AlphabetProfile: {name!r}") from exc


def _build_genome(document: GpmDocument) -> bytes:
    genome = bytearray()
    for entry in document.header:
        canonical = _encode_utf8(entry.word_canonical, field="Canonical")
        normalized = _encode_utf8(entry.word_normalized, field="Normalisiert")
        s_class = substance_width_class(entry.substance)
        s_bytes = width_bytes_for_class(s_class)
        genome += struct.pack("<H", len(canonical)) + canonical
        genome += struct.pack("<H", len(normalized)) + normalized
        genome += struct.pack("<B", s_class & 0x03)
        try:
            genome += encode_fixed_int(entry.substance, s_bytes)
        except ValueError as exc:
            raise GpmFormatError(str(exc)) from exc
    return bytes(genome)


def _build_body(document: GpmDocument) -> bytes:
    body = bytearray()
    for token in document.tokens:
        if token.word_id >= len(document.header):
            raise GpmFormatError(f"Ungültige Word-ID {token.word_id}.")
        entry = document.header[token.word_id]
        n = perm_space_size(entry.word_normalized)
        if not 1 <= token.perm_index <= n:
            raise GpmFormatError(
                f"Index I={token.perm_index} außerhalb N={n}."
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


def _build_registry_c(document: GpmDocument) -> bytes:
    from analysis.blocks.context import COrigin

    if document.registry is None:
        return struct.pack("<H", 0)
    block = bytearray()
    entries = document.registry.c_entries
    block += struct.pack("<H", len(entries))
    for entry in entries:
        origin_byte = 0 if entry.origin is COrigin.GEOM else 1
        block += struct.pack("<B", origin_byte)
        key = entry.key_bytes
        block += struct.pack("<H", len(key)) + key
        s_class = substance_width_class(max(1, entry.substance))
        s_bytes = width_bytes_for_class(s_class)
        block += struct.pack("<B", s_class & 0x03)
        block += encode_fixed_int(max(1, entry.substance), s_bytes)
        i_bytes = 2
        if entry.perm_space > 1:
            i_bytes = perm_width_bytes("A" * min(20, entry.perm_space))
        block += encode_fixed_int(max(1, entry.perm_index), i_bytes)
    return bytes(block)


def _read_registry_c(data: bytes, offset: int, body_end: int) -> int:
    if offset + 2 > body_end:
        raise GpmFormatError("Registry-C fehlt.")
    (c_count,) = struct.unpack_from("<H", data, offset)
    offset += 2
    for _ in range(c_count):
        if offset + 3 > body_end:
            raise GpmFormatError("C-Eintrag abgeschnitten.")
        offset += 1  # origin
        (klen,) = struct.unpack_from("<H", data, offset)
        offset += 2
        if offset + klen + 1 > body_end:
            raise GpmFormatError("C-Key abgeschnitten.")
        offset += klen
        s_class = data[offset] & 0x03
        offset += 1
        s_bytes = width_bytes_for_class(s_class)
        if offset + s_bytes > body_end:
            raise GpmFormatError("C-Substanz abgeschnitten.")
        offset += s_bytes
        i_bytes = 2
        if offset + i_bytes > body_end:
            raise GpmFormatError("C-Perm-Index abgeschnitten.")
        offset += i_bytes
    return offset


def write_gpm(
    document: GpmDocument,
    *,
    version: int | None = None,
    use_gap_rle: bool = False,
) -> bytes:
    """Schreibt .gpm (Standard: v9 mit Geometrie; v8/v4 weiter unterstützt)."""
    target_version = VERSION if version is None else version
    if target_version not in (VERSION, VERSION_V8, VERSION_V4):
        raise GpmFormatError(f"Schreiben für Version {target_version} nicht unterstützt.")

    assert_gap_symmetry(document)

    if len(document.header) > MAX_HEADER_ENTRIES:
        raise GpmFormatError("Zu viele Wörter im Header.")
    if len(document.tokens) > MAX_BODY_TOKENS:
        raise GpmFormatError("Zu viele Token im Body.")

    profile_block = b""
    flags = 0
    registry_c_block = b""
    if target_version in (VERSION, VERSION_V8):
        profile_block = _profile_to_bytes(document.profile)
        flags |= FLAG_PROFILE

    if target_version == VERSION:
        from analysis.blocks.build import materialize_geometry
        from analysis.reconstruct.derive_gaps import ensure_lossless_gaps

        materialize_geometry(document)
        flags |= FLAG_FRACTAL | FLAG_BODY_CELL | FLAG_BODY_HIER
        registry_c_block = _build_registry_c(document)
        if document.hierarchy is not None:
            gap_map = ensure_lossless_gaps(document)
            document.gap_rle = gap_map

    genome = _build_genome(document)
    body = _build_body(document)
    explicit = _build_explicit(document)

    if use_gap_rle:
        middle_blob = encode_full_gaps(document.gaps)
        flags |= FLAG_GAP_RLE
        perm = 0
    elif target_version == VERSION and document.gap_rle:
        from analysis.binary.gap_rle import encode_gap_rle

        middle_blob = encode_gap_rle(document.gap_rle)
        flags |= FLAG_GAP_RLE
        perm = 0
    else:
        perm = scan_perm_code(document.gaps)
        middle_blob = encode_gaps(document.gaps, perm)

    if len(middle_blob) > MAX_MIDDLE_BYTES:
        raise GpmFormatError("Separator/GAP-Block zu groß.")

    payload = profile_block + registry_c_block + genome + body + middle_blob + explicit

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


def _read_header_payload(data: bytes) -> tuple[int, int, int, int, int, int, int]:
    if len(data) < FILE_HEADER_SIZE + 4:
        raise GpmFormatError("Datei zu kurz.")

    stored_crc = struct.unpack_from("<I", data, len(data) - 4)[0]
    actual_crc = zlib.crc32(data[: len(data) - 4]) & 0xFFFFFFFF
    if stored_crc != actual_crc:
        raise GpmFormatError("CRC-Prüfsumme stimmt nicht — Datei beschädigt.")

    (
        version,
        flags,
        header_count,
        body_count,
        field_a,
        explicit_count,
        middle_len,
        payload_len,
    ) = struct.unpack_from("<BBIIIIII", data, 3)

    body_end = len(data) - 4
    expected_payload = body_end - FILE_HEADER_SIZE
    if payload_len != expected_payload:
        raise GpmFormatError("Payload-Länge inkonsistent.")

    return version, flags, header_count, body_count, field_a, explicit_count, middle_len, body_end


def _read_genome(
    data: bytes,
    offset: int,
    body_end: int,
    header_count: int,
) -> tuple[list[GpmHeaderEntry], int]:
    header: list[GpmHeaderEntry] = []

    def need(n: int) -> None:
        if offset + n > body_end:
            raise GpmFormatError("Datei unerwartet zu Ende.")

    for word_id in range(header_count):
        need(2)
        (orig_len,) = struct.unpack_from("<H", data, offset)
        offset += 2
        need(orig_len)
        canonical = data[offset : offset + orig_len].decode("utf-8")
        offset += orig_len

        need(2)
        (norm_len,) = struct.unpack_from("<H", data, offset)
        offset += 2
        need(norm_len)
        normalized = data[offset : offset + norm_len].decode("utf-8")
        offset += norm_len

        need(1)
        (s_flags,) = struct.unpack_from("<B", data, offset)
        offset += 1
        s_class = s_flags & 0x03
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
                word_canonical=canonical,
                word_normalized=normalized,
                substance=substance,
                perm_index=0,
            )
        )

    return header, offset


def _read_tokens(
    data: bytes,
    offset: int,
    body_end: int,
    header: list[GpmHeaderEntry],
    body_count: int,
) -> tuple[list[GpmToken], int]:
    tokens: list[GpmToken] = []

    def need(n: int) -> None:
        if offset + n > body_end:
            raise GpmFormatError("Datei unerwartet zu Ende.")

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
        tokens.append(
            GpmToken(
                word_id=word_id,
                perm_index=perm_index,
                case_code=case_code,
                payload_kind=PayloadKind.S,
            )
        )

    return tokens, offset


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
        need(text_len)
        explicit.append((token_index, data[offset : offset + text_len].decode("utf-8")))
        offset += text_len

    return explicit, offset


def read_gpm(data: bytes) -> GpmDocument:
    if len(data) < 5 or data[:3] != MAGIC_PREFIX:
        raise GpmFormatError("Keine gültige .gpm-Datei (Magic fehlt).")

    version = data[3]
    if version == VERSION:
        return _read_v9(data)
    if version == VERSION_V8:
        return _read_v8(data)
    if version == VERSION_V4:
        return _read_v4(data)
    raise GpmFormatError(f"Nicht unterstützte Version: {version}.")


def _read_v9(data: bytes) -> GpmDocument:
    (
        version,
        flags,
        header_count,
        body_count,
        separator_perm,
        explicit_count,
        middle_len,
        body_end,
    ) = _read_header_payload(data)

    if version != VERSION:
        raise GpmFormatError(f"Versionskonflikt: {version}.")

    offset = FILE_HEADER_SIZE
    profile = AlphabetProfile.OG
    if flags & FLAG_PROFILE:
        profile, offset = _profile_from_bytes(data, offset)

    if flags & FLAG_FRACTAL:
        offset = _read_registry_c(data, offset, body_end)

    header, offset = _read_genome(data, offset, body_end, header_count)
    tokens, offset = _read_tokens(data, offset, body_end, header, body_count)

    if offset + middle_len > body_end:
        raise GpmFormatError("Middle-Block abgeschnitten.")
    middle_blob = data[offset : offset + middle_len]
    offset += middle_len

    gap_count = body_count + 1
    if flags & FLAG_GAP_RLE:
        from analysis.binary.gap_rle import decode_gap_rle
        from analysis.hierarchy.geom import build_document_hierarchy
        from analysis.reconstruct.derive_gaps import derive_gaps, merge_gaps

        gap_rle = decode_gap_rle(middle_blob)
        if flags & (FLAG_BODY_HIER | FLAG_FRACTAL) and len(gap_rle) < gap_count:
            temp_doc = GpmDocument(
                profile=profile,
                header=header,
                tokens=tokens,
                gaps=[""] * gap_count,
                explicit=[],
                case_policy=DEFAULT_CASE_POLICY,
            )
            hierarchy = build_document_hierarchy(temp_doc)
            derived = derive_gaps(body_count, hierarchy)
            gaps = merge_gaps(derived, gap_rle)
        else:
            gaps = [gap_rle.get(i, "") for i in range(gap_count)]
    else:
        gaps = decode_gaps(middle_blob, separator_perm, gap_count)

    explicit, offset = _read_explicit(data, offset, body_end, explicit_count, tokens)

    if offset != body_end:
        raise GpmFormatError("Überhängende Bytes im Payload.")

    document = GpmDocument(
        profile=profile,
        header=header,
        tokens=tokens,
        gaps=gaps,
        explicit=explicit,
        case_policy=DEFAULT_CASE_POLICY,
    )
    from analysis.blocks.build import materialize_geometry

    materialize_geometry(document)
    assert_gap_symmetry(document)
    return document


def _read_v8(data: bytes) -> GpmDocument:
    (
        version,
        flags,
        header_count,
        body_count,
        separator_perm,
        explicit_count,
        middle_len,
        body_end,
    ) = _read_header_payload(data)

    if version != VERSION_V8:
        raise GpmFormatError(f"Versionskonflikt: {version}.")

    offset = FILE_HEADER_SIZE
    profile = AlphabetProfile.OG
    if flags & FLAG_PROFILE:
        profile, offset = _profile_from_bytes(data, offset)

    header, offset = _read_genome(data, offset, body_end, header_count)
    tokens, offset = _read_tokens(data, offset, body_end, header, body_count)

    if offset + middle_len > body_end:
        raise GpmFormatError("Middle-Block abgeschnitten.")
    middle_blob = data[offset : offset + middle_len]
    offset += middle_len

    gap_count = body_count + 1
    if flags & FLAG_GAP_RLE:
        try:
            gaps = decode_full_gaps(middle_blob, gap_count)
        except ValueError as exc:
            raise GpmFormatError(str(exc)) from exc
    else:
        try:
            gaps = decode_gaps(middle_blob, separator_perm, gap_count)
        except ValueError as exc:
            raise GpmFormatError(str(exc)) from exc

    explicit, offset = _read_explicit(data, offset, body_end, explicit_count, tokens)

    if offset != body_end:
        raise GpmFormatError("Überhängende Bytes im Payload.")

    document = GpmDocument(
        profile=profile,
        header=header,
        tokens=tokens,
        gaps=gaps,
        explicit=explicit,
        case_policy=DEFAULT_CASE_POLICY,
    )
    assert_gap_symmetry(document)
    return document


def _read_v4(data: bytes) -> GpmDocument:
    (
        version,
        _flags,
        header_count,
        body_count,
        separator_perm,
        explicit_count,
        separator_len,
        body_end,
    ) = _read_header_payload(data)

    if version != VERSION_V4:
        raise GpmFormatError(f"Versionskonflikt: {version}.")

    offset = FILE_HEADER_SIZE
    header, offset = _read_genome(data, offset, body_end, header_count)
    tokens, offset = _read_tokens(data, offset, body_end, header, body_count)

    if offset + separator_len > body_end:
        raise GpmFormatError("Separator-Block abgeschnitten.")
    separator_blob = data[offset : offset + separator_len]
    offset += separator_len

    gap_count = body_count + 1
    try:
        gaps = decode_gaps(separator_blob, separator_perm, gap_count)
    except ValueError as exc:
        raise GpmFormatError(str(exc)) from exc

    explicit, offset = _read_explicit(data, offset, body_end, explicit_count, tokens)

    if offset != body_end:
        raise GpmFormatError("Überhängende Bytes im Payload.")

    document = GpmDocument(
        profile=AlphabetProfile.OG,
        header=header,
        tokens=tokens,
        gaps=gaps,
        explicit=explicit,
        case_policy=DEFAULT_CASE_POLICY,
    )
    assert_gap_symmetry(document)
    return document
