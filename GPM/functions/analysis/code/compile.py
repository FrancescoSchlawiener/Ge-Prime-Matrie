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
from analysis.code.languages import language_for_extension, language_for_id
from analysis.code.tokenizer import tokenize_source
from analysis.code.tokens import tokenize_results_equal
from analysis.compile.compiler import compile_text
from analysis.compile.reconstruct import reconstruct_text
from analysis.document.model import GpmDocument


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
            lang = raw.language_id or "py"
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
