"""Text → GpmDocument (Phase 4a — verlustfrei, Gap-Symmetrie)."""

from __future__ import annotations

import unicodedata

from alphabets import AlphabetProfile
from alphabets.normalize import is_valid_substrate, prepare_substrate
from analysis.case.apply import apply_case
from analysis.case.codes import CASE_EXPLICIT, CASE_LOWER
from analysis.case.detect import detect_case
from analysis.case.policy import CaseStoragePolicy, DEFAULT_CASE_POLICY
from analysis.compile.tokenize import split_segments
from analysis.blocks.build import materialize_geometry
from analysis.document.invariants import assert_gap_symmetry
from analysis.document.model import CompileStats, GpmDocument, GpmHeaderEntry, GpmToken
from gpm_types.classify import PayloadKind, classify_token
from gpm_types.si import encode_si

MAX_COMPILE_TOKENS = 100_000


def normalize_text_nfc(text: str) -> str:
    text = unicodedata.normalize("NFC", text or "")
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _process_word_chunk(chunk: str, profile: AlphabetProfile) -> tuple[str, str, int, int] | None:
    try:
        kind = classify_token(chunk)
    except ValueError:
        return None
    if kind is not PayloadKind.S:
        return None
    normalized = prepare_substrate(chunk, profile)
    if not is_valid_substrate(normalized, profile):
        return None
    try:
        substance, perm_index = encode_si(chunk, profile)
    except ValueError:
        return None
    canonical = apply_case(chunk, CASE_LOWER)
    return canonical, normalized, substance, perm_index


def compile_text(
    text: str,
    profile: AlphabetProfile | str = AlphabetProfile.OG,
    *,
    case_policy: CaseStoragePolicy | None = None,
) -> tuple[GpmDocument, CompileStats]:
    if not text or not text.strip():
        raise ValueError("Leerer Text — nichts zu kompilieren.")

    if isinstance(profile, str):
        profile = AlphabetProfile(profile)
    policy = case_policy or DEFAULT_CASE_POLICY

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
            raise ValueError(f"Maximal {MAX_COMPILE_TOKENS:,} Wörter pro Dokument.")

        processed = _process_word_chunk(chunk, profile)
        if processed is None:
            pending_gap += chunk
            skipped += 1
            continue

        canonical, normalized, substance, perm_index = processed
        if canonical not in dictionary:
            word_id = len(header)
            dictionary[canonical] = word_id
            header.append(
                GpmHeaderEntry(
                    word_id=word_id,
                    word_canonical=canonical,
                    word_normalized=normalized,
                    substance=substance,
                    perm_index=perm_index,
                )
            )
        word_id = dictionary[canonical]

        if policy.store_case:
            code = detect_case(chunk)
        else:
            code = CASE_LOWER

        token_index = len(tokens)
        gaps.append(pending_gap)
        pending_gap = ""

        payload_kind = classify_token(chunk)
        tokens.append(
            GpmToken(
                word_id=word_id,
                perm_index=perm_index,
                case_code=code,
                payload_kind=payload_kind,
            )
        )
        if policy.store_case and code == CASE_EXPLICIT:
            explicit.append((token_index, chunk))

        word_count += 1

    gaps.append(pending_gap)

    if not tokens:
        raise ValueError("Kein Wort konnte encodiert werden.")

    document = GpmDocument(
        profile=profile,
        header=header,
        tokens=tokens,
        gaps=gaps,
        explicit=explicit,
        case_policy=policy,
    )
    assert_gap_symmetry(document)

    stats = CompileStats(
        word_count=word_count,
        skipped=skipped,
        explicit_count=len(explicit),
    )
    return document, stats


def compile_text_to_gpm(
    text: str,
    profile: AlphabetProfile | str = AlphabetProfile.OG,
    *,
    case_policy: CaseStoragePolicy | None = None,
    version: int | None = None,
    use_gap_rle: bool = False,
) -> tuple[GpmDocument, bytes, CompileStats]:
    """Kompiliert Text und serialisiert nach .gpm (v10 Standard)."""
    from analysis.binary.format import FILE_HEADER_SIZE, VERSION, VERSION_V9, write_gpm
    from analysis.binary.int_codec import (
        genome_substance_field_bytes,
        perm_width_bytes,
        perm_width_bytes_from_substance,
    )

    document, stats = compile_text(text, profile, case_policy=case_policy)
    materialize_geometry(document)
    blob = write_gpm(document, version=version, use_gap_rle=use_gap_rle)

    target_version = VERSION if version is None else version
    if target_version == VERSION:
        genome_bytes = sum(
            genome_substance_field_bytes(e.substance)
            + perm_width_bytes_from_substance(e.substance, document.profile)
            for e in document.header
        )
        body_bytes = 3 * len(document.tokens)
    else:
        genome_bytes = sum(
            4
            + len(e.word_canonical.encode("utf-8"))
            + len(e.word_normalized.encode("utf-8"))
            + genome_substance_field_bytes(e.substance)
            for e in document.header
        )
        body_bytes = sum(
            3 + perm_width_bytes(document.header[t.word_id].word_normalized)
            for t in document.tokens
        )
    explicit_bytes = sum(8 + len(text.encode("utf-8")) for _, text in document.explicit)
    profile_bytes = 1 + len(document.profile.value.encode("utf-8"))

    stats.file_bytes = len(blob)
    stats.genome_bytes = genome_bytes
    stats.body_bytes = body_bytes
    stats.explicit_bytes = explicit_bytes
    stats.profile_bytes = profile_bytes
    stats.separator_bytes = (
        len(blob) - FILE_HEADER_SIZE - profile_bytes - genome_bytes - body_bytes - explicit_bytes - 4
    )
    return document, blob, stats
