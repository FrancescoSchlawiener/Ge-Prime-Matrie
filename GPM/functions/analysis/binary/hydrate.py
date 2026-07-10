"""Header-/Token-Hydration nach v10-Lesen (S/I → abgeleitete Strings)."""

from __future__ import annotations

from alphabets import AlphabetProfile
from analysis.case.apply import apply_case
from analysis.case.codes import CASE_LOWER
from analysis.document.model import GpmDocument, GpmHeaderEntry, GpmToken
from gpm_types.si.codec import decode_si


def _derived_canonical(substance: int, perm_index: int, profile: AlphabetProfile | str) -> str:
    normalized = decode_si(substance, perm_index, profile)
    return apply_case(normalized, CASE_LOWER)


def hydrate_header_entry(entry: GpmHeaderEntry, profile: AlphabetProfile | str) -> GpmHeaderEntry:
    if entry.word_canonical and entry.word_normalized:
        return entry
    normalized = decode_si(entry.substance, entry.perm_index, profile)
    canonical = entry.word_canonical or apply_case(normalized, CASE_LOWER)
    return GpmHeaderEntry(
        word_id=entry.word_id,
        word_canonical=canonical,
        word_normalized=normalized,
        substance=entry.substance,
        perm_index=entry.perm_index,
    )


def hydrate_document(document: GpmDocument) -> GpmDocument:
    profile = document.profile
    document.header = [hydrate_header_entry(e, profile) for e in document.header]
    hydrated_tokens: list[GpmToken] = []
    for token in document.tokens:
        entry = document.header[token.word_id]
        hydrated_tokens.append(
            GpmToken(
                word_id=token.word_id,
                perm_index=entry.perm_index,
                case_code=token.case_code,
                payload_kind=token.payload_kind,
            )
        )
    document.tokens = hydrated_tokens
    return document
