"""Lesen und Analysieren von .gpm-Blobs."""

from __future__ import annotations

from dataclasses import dataclass

from analysis.binary.format import (
    FILE_HEADER_SIZE,
    GpmFormatError,
    MAGIC_PREFIX,
    read_gpm,
)
from analysis.compile.reconstruct import reconstruct_text
from analysis.document.model import GpmDocument


@dataclass
class GpmAnalysis:
    version: int
    flags: int
    header_count: int
    body_count: int
    explicit_count: int
    middle_len: int
    file_bytes: int
    reconstructed: str


def load_gpm(data: bytes) -> GpmDocument:
    return read_gpm(data)


def analyze_gpm(data: bytes) -> GpmAnalysis:
    if len(data) < 5 or data[:3] != MAGIC_PREFIX:
        raise GpmFormatError("Keine gültige .gpm-Datei.")
    import struct

    version, flags = struct.unpack_from("<BB", data, 3)
    header_count, body_count, _perm, explicit_count, middle_len = struct.unpack_from(
        "<IIIII", data, 5
    )
    document = read_gpm(data)
    return GpmAnalysis(
        version=version,
        flags=flags,
        header_count=header_count,
        body_count=body_count,
        explicit_count=explicit_count,
        middle_len=middle_len,
        file_bytes=len(data),
        reconstructed=reconstruct_text(document),
    )
