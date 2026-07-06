"""Job API routes — async Langoperationen mit Fortschritt."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alphabets import AlphabetProfile
from analysis.basis.index import build_basis_index, extend_basis_index
from analysis.redundancy.scan import scan_redundancy
from api.compile_service import compile_with_cache
from api.jobs.runner import job_runner, job_to_dict
from api.schemas.common import WorkbenchError
from api.schemas.requests import (
    CompileRequest,
    CorpusIndexRequest,
    JobCompileRequest,
    JobCorpusIndexRequest,
    JobRedundancyRequest,
    RedundancyScanRequest,
)
from api.session import store

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("/{job_id}")
def get_job(job_id: str) -> dict:
    rec = job_runner.get(job_id)
    if rec is None:
        raise WorkbenchError("job_not_found", f"Unbekannte job_id: {job_id!r}", status_code=404)
    return job_to_dict(rec)


@router.post("/compile")
def job_compile(req: JobCompileRequest) -> dict:
    job_id = job_runner.create("compile")
    compile_req = CompileRequest(
        mode=req.mode,
        text=req.text,
        profile=req.profile,
        language_id=req.language_id,
        content_key=req.content_key,
    )

    def worker(progress) -> dict:
        progress("compile", 20, "Kompiliere …")
        resp = compile_with_cache(compile_req)
        progress("compile", 100, "Kompilierung abgeschlossen")
        return {"response": resp.model_dump()}

    job_runner.run_async(job_id, worker)
    return {"job_id": job_id, "status": "pending"}


@router.post("/redundancy/scan")
def job_redundancy(req: JobRedundancyRequest) -> dict:
    try:
        stored = store.get_document(req.document_ref)
    except KeyError as exc:
        raise WorkbenchError("document_ref_not_found", str(exc), status_code=404) from exc
    if stored.document is None:
        raise WorkbenchError("value_error", "Kein Dokument für Redundanz-Scan.", status_code=400)

    job_id = job_runner.create("redundancy")
    doc = stored.document
    scan_kwargs = req.model_dump(exclude={"document_ref"})

    def worker(progress) -> dict:
        progress("index", 10, "Substance-Index …")

        def cb(phase: str, pct: int, msg: str) -> None:
            progress(phase, pct, msg)

        result = scan_redundancy(doc, progress_callback=cb, **scan_kwargs)
        return result

    job_runner.run_async(job_id, worker)
    return {"job_id": job_id, "status": "pending"}


@router.post("/corpus/index")
def job_corpus_index(req: JobCorpusIndexRequest) -> dict:
    job_id = job_runner.create("corpus_index")
    profile = AlphabetProfile(req.profile)

    def worker(progress) -> dict:
        docs = []
        total = len(req.document_refs)
        for i, ref in enumerate(req.document_refs):
            progress("load", int(10 + 70 * i / max(total, 1)), f"Lade Dokument {i + 1}/{total}")
            stored = store.get_document(ref)
            if stored.document is None:
                raise ValueError(f"Dokument {ref} nicht kompiliert.")
            docs.append((ref, stored.document))
        progress("index", 85, "Basis-Index …")
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
        progress("index", 100, "Index fertig")
        return {"index_id": index_id, "document_count": len(doc_refs), "profile": profile.value}

    job_runner.run_async(job_id, worker)
    return {"job_id": job_id, "status": "pending"}
