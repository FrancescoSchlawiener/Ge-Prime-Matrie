"""Tensorraum routes — deprecated alias für /api/code."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alphabets import AlphabetProfile
from api.schemas.common import WorkbenchResponse
from api.schemas.requests import TensorraumCanonicalizeRequest
from api.steps.code import canonicalize_for_code

router = APIRouter(prefix="/api/tensorraum", tags=["tensorraum"])


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
