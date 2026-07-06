"""Compare routes — word pair, documents, i-curve, corpus, redundancy."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alphabets import AlphabetProfile
from analysis.basis.compare_tiered import CompareTier
from analysis.basis.corpus_compare import find_similar_documents
from analysis.basis.index import build_basis_index, extend_basis_index
from analysis.pair.analyze_word_pair import analyze_word_pair
from analysis.corpus.search import search_anagrams_for_word
from analysis.redundancy.scan import scan_redundancy
from api.cache.document_cache import content_hash_key, document_cache
from api.cache.word_compile import compile_word_cached, register_word_pair_cached, word_entry_from_cache
from api.compile_service import compile_with_cache
from api.schemas.common import Step, WorkbenchResponse
from api.schemas.requests import (
    AnagramSearchRequest,
    CompileRequest,
    CompareDocumentsInlineRequest,
    CompareDocumentsRequest,
    CorpusIndexRequest,
    CorpusQueryRequest,
    ICurveRequest,
    RedundancyScanRequest,
    WordPairRequest,
)
from api.session import store
from api.steps.curves import build_full_pair_result
from api.steps.substance import build_compare_words_steps
from api.steps.tiered import build_tiered_compare_steps

router = APIRouter(prefix="/api/compare", tags=["compare"])


def _doc_from_inline(payload) -> tuple:
    req = CompileRequest(
        mode=payload.mode,
        text=payload.text,
        profile=payload.profile,
        language_id=payload.language_id,
    )
    key = content_hash_key(req.mode, req.profile, req.text, req.language_id)
    cached = document_cache.get(key)
    if cached is not None:
        return cached.document, cached.profile
    resp = compile_with_cache(req)
    ref = resp.result["document_ref"]
    stored = store.get_document(ref)
    return stored.document, stored.profile


def _get_doc_pair(doc_a_ref: str, doc_b_ref: str):
    try:
        a = store.get_document(doc_a_ref)
        b = store.get_document(doc_b_ref)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if a.document is None or b.document is None:
        raise HTTPException(status_code=400, detail="Beide document_refs müssen kompilierte Dokumente haben.")
    return a.document, b.document


def _enrich_word_pair_result(result: dict, a: str, b: str, profile) -> dict:
    wa, wb = register_word_pair_cached(a, b, profile)
    enriched = dict(result)
    enriched.update(
        {
            "word1": wa["original"],
            "word2": wb["original"],
            "normalized1": wa["normalized"],
            "normalized2": wb["normalized"],
            "content_hash1": wa["content_hash"],
            "content_hash2": wb["content_hash"],
            "substance1": wa["substance"],
            "substance2": wb["substance"],
            "perm_index1": wa["perm_index"],
            "perm_index2": wb["perm_index"],
        }
    )
    return enriched


@router.post("/word-pair", response_model=WorkbenchResponse)
def word_pair(req: WordPairRequest) -> WorkbenchResponse:
    try:
        if req.mode == "diff":
            result = analyze_word_pair(req.a, req.b, req.profile)
            steps = [
                Step(
                    id="classify",
                    title="Wortpaar-Differenz",
                    detail="Klassifikation und Substanz-Vergleich.",
                    values={"classification": str(result["classification"])},
                )
            ]
        else:
            result, steps = build_compare_words_steps(req.a, req.b, req.profile)
        result = _enrich_word_pair_result(result, req.a, req.b, req.profile)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    explain = ["/erklaerungen/07-wortpaar-diff"]
    return WorkbenchResponse(result=result, steps=steps, explain_links=explain)


@router.post("/anagram-search", response_model=WorkbenchResponse)
def anagram_search(req: AnagramSearchRequest) -> WorkbenchResponse:
    try:
        result = search_anagrams_for_word(req.word, req.profile, limit=req.limit)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="roman_alpha_db_missing") from exc
    except ValueError as exc:
        code = str(exc)
        if code in ("empty_word", "not_roman_alpha"):
            raise HTTPException(status_code=400, detail=code) from exc
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        cached, _ = compile_word_cached(req.word, req.profile)
        entry = word_entry_from_cache(cached)
        result["content_hash"] = entry["content_hash"]
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    steps = [
        Step(
            id="encode_query",
            title="Suchwort kodieren",
            detail="S und I für Anagramm-Bucket.",
            values={
                "normalized": result["normalized"],
                "substance": result["substance"],
                "perm_index": result["perm_index"],
            },
        ),
        Step(
            id="corpus_lookup",
            title="Korpus-Abfrage",
            detail="Roman-Alpha-DB nach gleichem S, anderem I.",
            values={"hit_count": result["hit_count"], "db_name": result["db_name"]},
        ),
    ]
    return WorkbenchResponse(
        result=result,
        steps=steps,
        explain_links=["/erklaerungen/11-wortpaar-anagramm"],
    )


@router.post("/documents", response_model=WorkbenchResponse)
def compare_documents(req: CompareDocumentsRequest) -> WorkbenchResponse:
    doc_a, doc_b = _get_doc_pair(req.doc_a_ref, req.doc_b_ref)
    try:
        result, steps = build_tiered_compare_steps(doc_a, doc_b, req.tier)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return WorkbenchResponse(result=result, steps=steps, explain_links=["/erklaerungen/09-ggt-kgv"])


@router.post("/documents-inline", response_model=WorkbenchResponse)
def compare_documents_inline(req: CompareDocumentsInlineRequest) -> WorkbenchResponse:
    try:
        doc_a, _ = _doc_from_inline(req.doc_a)
        doc_b, _ = _doc_from_inline(req.doc_b)
        result, steps = build_tiered_compare_steps(doc_a, doc_b, req.tier)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return WorkbenchResponse(result=result, steps=steps)


@router.post("/i-curve", response_model=WorkbenchResponse)
def i_curve(req: ICurveRequest) -> WorkbenchResponse:
    doc_a, doc_b = _get_doc_pair(req.doc_a_ref, req.doc_b_ref)
    try:
        result, steps, meta = build_full_pair_result(doc_a, doc_b)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return WorkbenchResponse(
        result=result,
        steps=steps,
        curve_meta=meta,
        explain_links=["/erklaerungen/02-index-i"],
    )


@router.post("/corpus/index", response_model=WorkbenchResponse)
def corpus_index(req: CorpusIndexRequest) -> WorkbenchResponse:
    docs = []
    for ref in req.document_refs:
        try:
            stored = store.get_document(ref)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        if stored.document is None:
            raise HTTPException(status_code=400, detail=f"Dokument {ref} nicht kompiliert.")
        docs.append((ref, stored.document))
    profile = AlphabetProfile(req.profile)
    if req.extend_index_id:
        stored_idx = store.get_index(req.extend_index_id)
        partitions = stored_idx.partitions
        extend_basis_index(partitions, docs)
        stored_idx.doc_refs = list(dict.fromkeys(stored_idx.doc_refs + req.document_refs))
        index_id = req.extend_index_id
        doc_refs = stored_idx.doc_refs
    else:
        partitions = build_basis_index(docs)
        doc_refs = req.document_refs
        index_id = store.put_index(partitions, doc_refs, profile)
    return WorkbenchResponse(
        result={"index_id": index_id, "document_count": len(doc_refs), "profile": profile.value},
        steps=[Step(id="index", title="Basis-Index", detail="Korpus indexiert.", values={"count": len(doc_refs)})],
    )


@router.post("/corpus/query", response_model=WorkbenchResponse)
def corpus_query(req: CorpusQueryRequest) -> WorkbenchResponse:
    try:
        stored_index = store.get_index(req.index_id)
        stored_query = store.get_document(req.query_ref)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if stored_query.document is None:
        raise HTTPException(status_code=400, detail="Query-Dokument nicht kompiliert.")
    profile = stored_query.document.profile
    if profile not in stored_index.partitions:
        return WorkbenchResponse(result={"hits": [], "zero_reason": "profile_partition_empty"}, steps=[])
    max_tier = CompareTier(min(max(req.tier, 0), 4))

    def _load_doc(doc_id: str):
        stored = store.get_document(doc_id)
        return stored.document

    search = find_similar_documents(
        stored_query.document,
        max_tier=max_tier,
        top_k=req.top_k,
        index=stored_index.partitions,
        corpus_ids=stored_index.doc_refs,
        doc_loader=_load_doc,
    )
    hits = [
        {
            "doc_id": h.doc_id,
            "score": h.score,
            "zero_reason": h.zero_reason,
            "tiers_run": list(h.tiers_run),
            "shared_prime_count": h.shared_prime_count,
        }
        for h in search.hits
    ]
    return WorkbenchResponse(
        result={"hits": hits, "zero_reason": search.zero_reason},
        steps=[Step(id="query", title="Korpus-Abfrage", detail="Ähnliche Dokumente.", values={"hits": len(hits)})],
    )


@router.post("/redundancy/scan", response_model=WorkbenchResponse)
def redundancy_scan(req: RedundancyScanRequest) -> WorkbenchResponse:
    try:
        stored = store.get_document(req.document_ref)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if stored.document is None:
        raise HTTPException(status_code=400, detail="Kein Dokument für Redundanz-Scan.")
    try:
        result = scan_redundancy(
            stored.document,
            canonical=req.canonical,
            window_mode=req.window_mode,
            window_min=req.window_min,
            window_max=req.window_max,
            window_size=req.window_size,
            structural_only=req.structural_only,
            level=req.level,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return WorkbenchResponse(
        result=result,
        steps=[Step(id="redundancy", title="Redundanz-Scan", detail="Gleitende Fenster.", values={"chains": len(result.get("chains", []))})],
    )
