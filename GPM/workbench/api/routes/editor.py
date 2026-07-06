"""Editor routes — compile, reconstruct, gpm, spectroscope."""

from __future__ import annotations

import base64
import binascii

from fastapi import APIRouter

from analysis.binary.format import read_gpm, write_gpm
from analysis.binary.gpc import decrypt_gpm_file, is_encrypted_gpm_blob, wrap_cipher_payload
from analysis.code.decompile import reconstruct_hybrid, reconstruct_source
from analysis.compile.reconstruct import reconstruct_text
from analysis.search.spectroscope import spectroscope_analyze
from analysis.binary.search import search_by_gcd, search_by_lcm, search_by_word
from analysis.security.cipher import encrypt_text
from api.compile_service import compile_with_cache
from api.schemas.common import Step, WorkbenchError, WorkbenchResponse
from api.schemas.requests import (
    CompileRequest,
    GpmReadRequest,
    GpmSearchRequest,
    GpmWriteRequest,
    ReconstructRequest,
    SpectroscopeRequest,
)
from api.session import document_to_dict, gpm_bytes_to_b64, store

router = APIRouter(prefix="/api/editor", tags=["editor"])

GPM_MAGIC = b"GPM"


def _validate_gpm_blob(raw: bytes) -> None:
    if is_encrypted_gpm_blob(raw):
        raise WorkbenchError(
            "cipher_key_required",
            "Verschlüsselte GPC-Datei — Schlüssel erforderlich.",
            status_code=401,
        )
    if len(raw) < 12 or raw[:3] != GPM_MAGIC:
        raise WorkbenchError(
            "gpm_invalid_stream",
            "Ungültiger GPM-Stream (Magic oder Länge).",
            status_code=422,
        )


@router.post("/compile", response_model=WorkbenchResponse)
def compile_endpoint(req: CompileRequest) -> WorkbenchResponse:
    return compile_with_cache(req)


@router.post("/reconstruct", response_model=WorkbenchResponse)
def reconstruct_endpoint(req: ReconstructRequest) -> WorkbenchResponse:
    stored = store.get_document(req.document_ref)
    if stored.mode == "hybrid" and stored.hybrid is not None:
        text = reconstruct_hybrid(stored.hybrid)
    elif stored.mode == "code" and stored.document is not None and stored.document.registry is not None:
        text = reconstruct_source(stored.document.root_block, stored.document.registry)
    elif stored.document is not None:
        text = reconstruct_text(stored.document)
    else:
        raise WorkbenchError("value_error", "Kein rekonstruierbares Dokument.", status_code=400)

    return WorkbenchResponse(
        result={"text": text, "document_ref": req.document_ref},
        steps=[Step(id="reconstruct", title="Rekonstruktion", detail="Dokument → Quelltext.", values={"length": len(text)})],
    )


@router.post("/gpm/read", response_model=WorkbenchResponse)
def gpm_read(req: GpmReadRequest) -> WorkbenchResponse:
    raw = bytes(req.base64)
    if is_encrypted_gpm_blob(raw):
        if not req.key:
            raise WorkbenchError(
                "cipher_key_required",
                "Verschlüsselte GPC-Datei — Schlüssel erforderlich.",
                status_code=401,
            )
        try:
            dec = decrypt_gpm_file(raw, keys_raw=req.key)
        except ValueError as exc:
            raise WorkbenchError("value_error", str(exc), status_code=400) from exc
        dec_text = dec["text"]
        try:
            inner = base64.b64decode(dec_text.strip().encode("ascii"), validate=True)
            if len(inner) >= 3 and inner[:3] == GPM_MAGIC:
                raw = inner
            else:
                return WorkbenchResponse(
                    result={"reconstructed_text": dec_text, "token_count": dec.get("token_count", 0)},
                    steps=[
                        Step(
                            id="gpm_decrypt",
                            title="GPC entschlüsselt",
                            detail="Klartext geladen.",
                            values={"tokens": dec.get("token_count", 0)},
                        )
                    ],
                )
        except (ValueError, binascii.Error):
            return WorkbenchResponse(
                result={"reconstructed_text": dec_text, "token_count": dec.get("token_count", 0)},
                steps=[
                    Step(
                        id="gpm_decrypt",
                        title="GPC entschlüsselt",
                        detail="Klartext geladen.",
                        values={"tokens": dec.get("token_count", 0)},
                    )
                ],
            )
    _validate_gpm_blob(raw)
    try:
        doc = read_gpm(raw)
    except Exception as exc:
        raise WorkbenchError(
            "gpm_invalid_stream",
            str(exc),
            status_code=422,
        ) from exc
    ref = store.put_document(mode="gpm", profile=doc.profile, document=doc, gpm_bytes=raw)
    if doc.registry is not None and doc.root_block is not None:
        text = reconstruct_source(doc.root_block, doc.registry)
    else:
        text = reconstruct_text(doc)
    return WorkbenchResponse(
        result={
            **document_to_dict(doc),
            "document_ref": ref,
            "base64_size": len(raw),
            "reconstructed_text": text,
        },
        steps=[Step(id="gpm_read", title="GPM lesen", detail="Binärdatei dekodiert.", values={"tokens": len(doc.tokens)})],
    )


@router.post("/gpm/write", response_model=WorkbenchResponse)
def gpm_write(req: GpmWriteRequest) -> WorkbenchResponse:
    stored = store.get_document(req.document_ref)
    if stored.document is None:
        raise WorkbenchError("value_error", "Kein Dokument für GPM-Export.", status_code=400)
    try:
        data = write_gpm(stored.document)
        read_gpm(data)
    except Exception as exc:
        raise WorkbenchError(
            "gpm_invalid_stream",
            f"GPM Round-Trip fehlgeschlagen: {exc}",
            status_code=500,
        ) from exc

    if req.encrypt:
        if not req.key:
            raise WorkbenchError(
                "cipher_key_required",
                "Verschlüsselung erfordert key.",
                status_code=401,
            )
        b64 = gpm_bytes_to_b64(data)
        enc = encrypt_text(b64, mode="word", keys_raw=req.key)
        data = wrap_cipher_payload(enc["ciphertext"], mode="word")

    stored.gpm_bytes = data
    return WorkbenchResponse(
        result={
            "base64": gpm_bytes_to_b64(data),
            "bytes": len(data),
            "document_ref": req.document_ref,
            "encrypted": req.encrypt,
        },
        steps=[Step(id="gpm_write", title="GPM schreiben", detail="Dokument serialisiert.", values={"bytes": len(data)})],
    )


@router.post("/gpm/search", response_model=WorkbenchResponse)
def gpm_search(req: GpmSearchRequest) -> WorkbenchResponse:
    stored = store.get_document(req.document_ref)
    if stored.document is None:
        raise WorkbenchError("value_error", "Kein Dokument für Suche.", status_code=400)
    try:
        if req.mode == "gcd":
            result = search_by_gcd(stored.document, req.query)
        elif req.mode == "lcm":
            queries = req.queries or ([req.query] if req.query else [])
            result = search_by_lcm(stored.document, *queries)
        else:
            result = search_by_word(stored.document, req.query)
    except ValueError as exc:
        raise WorkbenchError("value_error", str(exc), status_code=400) from exc
    return WorkbenchResponse(
        result=result,
        steps=[Step(id="gpm_search", title="Genom-Suche", detail=f"Modus: {req.mode}.", values={"mode": req.mode})],
    )


@router.post("/spectroscope", response_model=WorkbenchResponse)
def spectroscope_endpoint(req: SpectroscopeRequest) -> WorkbenchResponse:
    stored = store.get_document(req.document_ref)
    if stored.document is None:
        raise WorkbenchError("value_error", "Kein Dokument für Spectroscope.", status_code=400)
    if req.content_key and stored.document is not None:
        from api.cache.document_cache import document_cache

        cached = document_cache.get(req.content_key)
        if cached is None:
            raise WorkbenchError(
                "cache_miss",
                "content_key passt nicht zur Session.",
                status_code=400,
            )
    result = spectroscope_analyze(
        stored.document,
        token_start=req.token_start,
        token_end=req.token_end or len(stored.document.tokens),
    )
    return WorkbenchResponse(
        result=result,
        steps=[Step(id="spectroscope", title="Spectroscope", detail="Fenster-Analyse auf Token-Span.", values={"matches": len(result.get("matches", []))})],
    )
