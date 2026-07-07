"""Zentraler Compile-Pfad mit CAS-Cache."""

from __future__ import annotations

from alphabets import AlphabetProfile
from analysis.blocks.registry import DocumentRegistry
from analysis.code.compile import (
    compile_hybrid,
    compile_source,
    hybrid_to_gpm_document,
    verify_hybrid_reversibility,
)
from analysis.code.decompile import reconstruct_source
from analysis.compile.compiler import compile_text
from analysis.compile.reconstruct import reconstruct_text
from analysis.document.model import GpmDocument
from analysis.inference.trace import InferenceTrace
from api.cache.document_cache import CachedCompileEntry, content_hash_key, document_cache
from api.schemas.common import WorkbenchResponse, WorkbenchError
from api.schemas.requests import CompileRequest
from api.session import store
from api.steps.compile import map_code_compile_steps, map_hybrid_compile_steps, map_nl_compile_steps
from api.steps.hybrid import build_code_payload, build_hybrid_payload, build_nl_payload


def _resolve_profile(value: str) -> AlphabetProfile:
    return AlphabetProfile(value)


def _compile_entry(req: CompileRequest) -> CachedCompileEntry:
    profile = _resolve_profile(req.profile)
    text = req.text
    if req.mode == "nl":
        doc, stats = compile_text(text, profile)
        trace = InferenceTrace(compile_stats=stats, normalized=text)
        return CachedCompileEntry(
            content_hash="",
            mode="nl",
            profile=profile,
            document=doc,
            source_text=text,
            stats=stats,
            trace=trace,
        )
    if req.mode == "code":
        lang = req.language_id or "py"
        reg = DocumentRegistry(profile=profile)
        module = compile_source(text, lang, reg)
        doc = GpmDocument(profile=profile, header=[], tokens=[], gaps=[""])
        doc.registry = reg
        doc.root_block = module
        return CachedCompileEntry(
            content_hash="",
            mode="code",
            profile=profile,
            document=doc,
            source_text=text,
            language_id=lang,
        )
    hybrid = compile_hybrid(text, profile)
    gpm_doc = hybrid_to_gpm_document(hybrid)
    return CachedCompileEntry(
        content_hash="",
        mode="hybrid",
        profile=profile,
        document=gpm_doc,
        hybrid=hybrid,
        source_text=text,
    )


def compile_with_cache(req: CompileRequest) -> WorkbenchResponse:
    if req.content_key and not req.text:
        cached = document_cache.get(req.content_key)
        if cached is None:
            raise WorkbenchError(
                "cache_miss",
                "content_key ohne Treffer — text erforderlich.",
                status_code=400,
            )
        entry = cached
        cache_hit = True
    else:
        key = req.content_key or content_hash_key(
            req.mode, req.profile, req.text, req.language_id
        )

        def _build() -> CachedCompileEntry:
            built = _compile_entry(req)
            built.content_hash = key
            return built

        entry, cache_hit = document_cache.get_or_compile(key, _build)

    profile = entry.profile
    text = entry.source_text

    if entry.mode == "nl":
        reconstructed = reconstruct_text(entry.document)
        roundtrip_ok = reconstructed == text
        ref = store.put_document(
            mode="nl", profile=profile, document=entry.document, source_text=text
        )
        result = build_nl_payload(entry.document, document_ref=ref, roundtrip_ok=roundtrip_ok)
        result["reconstructed_text"] = reconstructed
        steps = map_nl_compile_steps(entry.stats, entry.trace) if entry.stats else map_nl_compile_steps(
            entry.trace.compile_stats, entry.trace
        )
    elif entry.mode == "code":
        reg = entry.document.registry
        reconstructed = reconstruct_source(entry.document.root_block, reg)
        roundtrip_ok = reconstructed == text
        lang = entry.language_id or "py"
        ref = store.put_document(
            mode="code",
            profile=profile,
            document=entry.document,
            source_text=text,
            language_id=lang,
        )
        registry_entries = [
            {
                "word_id": e.word_id,
                "word_canonical": e.word_canonical,
                "word_normalized": e.word_normalized,
                "substance": e.substance,
                "perm_index": e.perm_index,
            }
            for e in reg.s_entries
        ]
        result = build_code_payload(
            document_ref=ref,
            profile=profile.value,
            language_id=lang,
            registry_entries=registry_entries,
            roundtrip_ok=roundtrip_ok,
        )
        steps = map_code_compile_steps(lang, len(registry_entries))
    else:
        roundtrip_ok = verify_hybrid_reversibility(text, profile)
        ref = store.put_document(
            mode="hybrid",
            profile=profile,
            document=entry.document,
            hybrid=entry.hybrid,
            source_text=text,
        )
        result = build_hybrid_payload(entry.hybrid, document_ref=ref, roundtrip_ok=roundtrip_ok)
        steps = map_hybrid_compile_steps(
            len(entry.hybrid.segments),
            len(result["registry_entries"]),
            len(result.get("fence_boundaries", [])),
        )

    result["content_hash"] = entry.content_hash
    result["cache_hit"] = cache_hit
    result["roundtrip_details"] = {
        "nl_ok": entry.mode == "nl" and roundtrip_ok,
        "hybrid_ok": entry.mode == "hybrid" and roundtrip_ok,
        "byte_identical": roundtrip_ok,
    }
    return WorkbenchResponse(
        result=result,
        steps=steps,
        explain_links=["/erklaerungen/12-gaps-dokument"],
    )
