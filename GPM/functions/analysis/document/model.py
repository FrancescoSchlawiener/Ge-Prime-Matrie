"""In-Memory GPM-Dokumentmodell (Phase 4a)."""

from __future__ import annotations

from dataclasses import dataclass, field

from alphabets import AlphabetProfile
from analysis.case.policy import CaseStoragePolicy, DEFAULT_CASE_POLICY
from gpm_types.classify import PayloadKind


@dataclass
class GpmHeaderEntry:
    word_id: int
    word_canonical: str
    word_normalized: str
    substance: int
    perm_index: int


@dataclass
class GpmToken:
    word_id: int
    perm_index: int
    case_code: int
    payload_kind: PayloadKind = PayloadKind.S


@dataclass
class CompileStats:
    word_count: int = 0
    skipped: int = 0
    explicit_count: int = 0
    file_bytes: int = 0
    genome_bytes: int = 0
    body_bytes: int = 0
    separator_bytes: int = 0
    explicit_bytes: int = 0
    profile_bytes: int = 0


@dataclass
class GpmDocument:
    profile: AlphabetProfile
    header: list[GpmHeaderEntry]
    tokens: list[GpmToken]
    gaps: list[str]
    explicit: list[tuple[int, str]] = field(default_factory=list)
    case_policy: CaseStoragePolicy = DEFAULT_CASE_POLICY
