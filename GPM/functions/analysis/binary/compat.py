"""OG ↔ GPM Format-Brücke."""

from __future__ import annotations

from analysis.binary.format import GpmFormatError, read_gpm
from analysis.document.model import GpmDocument, GpmHeaderEntry, GpmToken

VERSION_V7 = 7


def read_gpm_any(data: bytes) -> GpmDocument:
    """Liest v4/v8/v9 nativ; v7 best-effort über v4-kompatibles Layout."""
    if len(data) < 4 or data[:3] != b"GPM":
        raise GpmFormatError("Keine GPM-Datei.")
    version = data[3]
    if version in (4, 8, 9):
        return read_gpm(data)
    if version == VERSION_V7:
        return _lift_v7(data)
    raise GpmFormatError(f"Nicht unterstützte Version: {version}.")


def _lift_v7(data: bytes) -> GpmDocument:
    """Hebt OG v7 auf GpmDocument — flaches Token-Body wie v4."""
    try:
        return read_gpm(data)
    except GpmFormatError:
        pass
    return _read_v7_flat(data)


def _read_v7_flat(data: bytes) -> GpmDocument:
    import struct

    from alphabets import AlphabetProfile
    from analysis.binary.format import FILE_HEADER_SIZE, _read_explicit, _read_genome, _read_header_payload, _read_tokens
    from analysis.binary.separator_codec import decode_gaps
    from analysis.case.policy import DEFAULT_CASE_POLICY

    (
        version,
        _flags,
        header_count,
        body_count,
        separator_perm,
        explicit_count,
        middle_len,
        body_end,
    ) = _read_header_payload(data)
    if version != VERSION_V7:
        raise GpmFormatError(f"Erwartete v7, erhielt {version}.")
    offset = FILE_HEADER_SIZE
    header, offset = _read_genome(data, offset, body_end, header_count)
    tokens, offset = _read_tokens(data, offset, body_end, header, body_count)
    middle_blob = data[offset : offset + middle_len]
    offset += middle_len
    gaps = decode_gaps(middle_blob, separator_perm, body_count + 1)
    explicit, offset = _read_explicit(data, offset, body_end, explicit_count, tokens)
    return GpmDocument(
        profile=AlphabetProfile.OG,
        header=header,
        tokens=tokens,
        gaps=gaps,
        explicit=explicit,
        case_policy=DEFAULT_CASE_POLICY,
    )


def convert_v7_header_entries(entries: list) -> list[GpmHeaderEntry]:
    """Mappt OG-Header-Einträge auf GPM/functions GpmHeaderEntry."""
    out: list[GpmHeaderEntry] = []
    for i, e in enumerate(entries):
        out.append(
            GpmHeaderEntry(
                word_id=i,
                word_canonical=getattr(e, "word_original", getattr(e, "word_canonical", "")),
                word_normalized=getattr(e, "word_normalized", ""),
                substance=getattr(e, "substance", 1),
                perm_index=getattr(e, "perm_index", 1),
            )
        )
    return out
