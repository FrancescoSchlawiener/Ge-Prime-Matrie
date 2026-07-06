"""Size compare API routes."""

from __future__ import annotations

from fastapi import APIRouter

from api.schemas.common import WorkbenchResponse
from api.schemas.requests import (
    SizeDecodeRequest,
    SizeEncodeBatchRequest,
    SizeEncodeWordRequest,
)
from api.size_service import (
    compare_decode_cached,
    compare_encode_batch_cached,
    compare_encode_word_cached,
)

router = APIRouter(prefix="/api/size", tags=["size"])


@router.post("/encode-word", response_model=WorkbenchResponse)
def size_encode_word(req: SizeEncodeWordRequest) -> WorkbenchResponse:
    fallback = req.fallback.model_dump() if req.fallback is not None else None
    result = compare_encode_word_cached(
        content_hash=req.content_hash,
        profile=req.profile,
        fallback=fallback,
    )
    return WorkbenchResponse(result=result)


@router.post("/encode-batch", response_model=WorkbenchResponse)
def size_encode_batch(req: SizeEncodeBatchRequest) -> WorkbenchResponse:
    result = compare_encode_batch_cached(word_hashes=req.word_hashes)
    return WorkbenchResponse(result=result)


@router.post("/decode", response_model=WorkbenchResponse)
def size_decode(req: SizeDecodeRequest) -> WorkbenchResponse:
    fallback = req.fallback.model_dump() if req.fallback is not None else None
    result = compare_decode_cached(
        content_hash=req.content_hash,
        profile=req.profile,
        fallback=fallback,
    )
    return WorkbenchResponse(result=result)
