"""Code kompilieren und Hybrid-Dokumente."""

from __future__ import annotations

import unicodedata
from pathlib import Path

from alphabets import AlphabetProfile
from alphabets.unicode_utils import assert_no_surrogates
from analysis.blocks.context import ParseDomain
from analysis.blocks.node import BlockNode
from analysis.blocks.registry import DocumentRegistry
from analysis.code.block_parser import parse_code_blocks
from analysis.code.context import scan_fences_hybrid
from analysis.code.decompile import reconstruct_hybrid, reconstruct_source
from analysis.code.hybrid import HybridDocument, HybridSegment
from analysis.code.languages import language_for_extension, language_for_id, resolve_fence_language
from analysis.code.tokenizer import tokenize_source
from analysis.code.tokens import tokenize_results_equal
from analysis.compile.compiler import compile_text
from analysis.compile.reconstruct import reconstruct_text
from analysis.document.model import GpmDocument, GpmHeaderEntry, GpmToken


def compile_source(source: str, language_id: str, registry: DocumentRegistry) -> BlockNode:
    assert_no_surrogates(source)
    source = unicodedata.normalize("NFC", source)
    language_for_id(language_id)
    return parse_code_blocks(source, language_id, registry)


def verify_reversibility(source: str, language_id: str, registry: DocumentRegistry) -> bool:
    assert_no_surrogates(source)
    source = unicodedata.normalize("NFC", source)
    orig = tokenize_source(source, language_id)
    module = compile_source(source, language_id, registry)
    decompiled = reconstruct_source(module, registry)
    if decompiled != source:
        return False
    return tokenize_results_equal(tokenize_source(decompiled, language_id), orig)


def _compile_nl_slice(text: str, profile: AlphabetProfile) -> GpmDocument:
    if not text.strip():
        return GpmDocument(profile=profile, header=[], tokens=[], gaps=[text] if text else [""])
    doc, _ = compile_text(text, profile)
    return doc


def compile_hybrid(text: str, profile: AlphabetProfile | str = AlphabetProfile.OG) -> HybridDocument:
    """Markdown mit Code-Fences — Gap-Erhaltungs-Invariante an Segmentgrenzen."""
    assert_no_surrogates(text)
    text = unicodedata.normalize("NFC", text)
    prof = profile if isinstance(profile, AlphabetProfile) else AlphabetProfile(profile)
    reg = DocumentRegistry(profile=prof)
    scanned = scan_fences_hybrid(text)
    segments: list[HybridSegment] = []

    for raw in scanned:
        if raw.domain is ParseDomain.NL:
            nl_doc = _compile_nl_slice(raw.body, prof)
            segments.append(
                HybridSegment(
                    domain=ParseDomain.NL,
                    source_start=raw.source_start,
                    source_end=raw.source_end,
                    nl_document=nl_doc,
                )
            )
        else:
            lang = resolve_fence_language(raw.language_id or "py")
            code_mod = compile_source(raw.body, lang, reg)
            segments.append(
                HybridSegment(
                    domain=ParseDomain.CODE,
                    source_start=raw.source_start,
                    source_end=raw.source_end,
                    language_id=lang,
                    fence_open=raw.fence_open,
                    fence_close=raw.fence_close,
                    code_module=code_mod,
                )
            )

    return HybridDocument(profile=prof, segments=segments, registry=reg)


def verify_hybrid_reversibility(text: str, profile: AlphabetProfile | str = AlphabetProfile.OG) -> bool:
    assert_no_surrogates(text)
    text = unicodedata.normalize("NFC", text)
    doc = compile_hybrid(text, profile)
    return reconstruct_hybrid(doc) == text


def compile_source_file(path: str | Path, registry: DocumentRegistry) -> BlockNode:
    p = Path(path)
    spec = language_for_extension(str(p))
    if spec is None:
        raise ValueError(f"Keine Sprache für Datei: {path}")
    source = p.read_text(encoding="utf-8")
    return compile_source(source, spec.id, registry)


def _merge_gpm_documents(docs: list[GpmDocument], profile: AlphabetProfile) -> GpmDocument:
    if not docs:
        return GpmDocument(profile=profile, header=[], tokens=[], gaps=[""])
    if len(docs) == 1:
        return docs[0]
    merged = GpmDocument(profile=profile, header=[], tokens=[], gaps=[""], explicit=[])
    token_offset = 0
    for doc in docs:
        id_map: dict[int, int] = {}
        for entry in doc.header:
            new_id = len(merged.header)
            id_map[entry.word_id] = new_id
            merged.header.append(
                GpmHeaderEntry(
                    word_id=new_id,
                    word_canonical=entry.word_canonical,
                    word_normalized=entry.word_normalized,
                    substance=entry.substance,
                    perm_index=entry.perm_index,
                )
            )
        if not doc.tokens:
            continue
        if merged.tokens:
            merged.gaps[-1] = merged.gaps[-1] + doc.gaps[0]
            gap_start = 1
        else:
            merged.gaps[0] = doc.gaps[0]
            gap_start = 0
        for tok in doc.tokens:
            merged.tokens.append(
                GpmToken(
                    word_id=id_map[tok.word_id],
                    perm_index=tok.perm_index,
                    case_code=tok.case_code,
                    payload_kind=tok.payload_kind,
                )
            )
        for gi in range(gap_start, len(doc.gaps)):
            merged.gaps.append(doc.gaps[gi])
        for idx, text in doc.explicit:
            merged.explicit.append((token_offset + idx, text))
        token_offset += len(doc.tokens)
    return merged


def hybrid_to_gpm_document(hybrid: HybridDocument) -> GpmDocument:
    """Hybrid → GpmDocument (NL-Body + Code-Registry/Block-Tree für v9)."""
    nl_docs = [s.nl_document for s in hybrid.segments if s.nl_document is not None]
    doc = _merge_gpm_documents(nl_docs, hybrid.profile)
    doc.registry = hybrid.registry
    for seg in hybrid.segments:
        if seg.code_module is not None:
            doc.root_block = seg.code_module
            break
    return doc


def compile_hybrid_to_gpm(
    text: str,
    profile: AlphabetProfile | str = AlphabetProfile.OG,
) -> tuple[GpmDocument, bytes]:
    hybrid = compile_hybrid(text, profile)
    doc = hybrid_to_gpm_document(hybrid)
    from analysis.binary.format import VERSION, write_gpm

    return doc, write_gpm(doc, version=VERSION)

