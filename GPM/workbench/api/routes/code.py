"""Code routes — Kanonisierung über GPM/functions (library-first)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alphabets import AlphabetProfile
from api.schemas.common import WorkbenchResponse
from api.schemas.requests import TensorraumCanonicalizeRequest
from api.steps.code import canonicalize_for_code, languages_payload
from analysis.code.manifest import language_manifest

router = APIRouter(prefix="/api/code", tags=["code"])


@router.get("/languages", response_model=WorkbenchResponse)
def languages_endpoint() -> WorkbenchResponse:
    return WorkbenchResponse(
        result=languages_payload(),
        explain_links=["/erklaerungen/24-code-blocks", "/erklaerungen/15-registry"],
    )


@router.post("/canonicalize", response_model=WorkbenchResponse)
def canonicalize_endpoint(req: TensorraumCanonicalizeRequest) -> WorkbenchResponse:
    try:
        profile = AlphabetProfile(req.profile)
        result = canonicalize_for_code(req.source, req.filename, profile=profile)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return WorkbenchResponse(
        result=result,
        explain_links=["/erklaerungen/24-code-blocks", "/erklaerungen/15-registry"],
    )


@router.post("/manifest", response_model=WorkbenchResponse)
def manifest_endpoint(req: TensorraumCanonicalizeRequest) -> WorkbenchResponse:
    try:
        result = language_manifest(req.source, req.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return WorkbenchResponse(result=result, explain_links=["/erklaerungen/24-code-blocks"])
