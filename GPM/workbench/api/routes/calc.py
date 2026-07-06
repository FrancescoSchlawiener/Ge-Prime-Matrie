"""Calc routes — encode, decode, compare words."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alphabets import AlphabetProfile
from api.schemas.common import WorkbenchResponse
from api.schemas.requests import CompareWordsRequest, DecodeWordRequest, EncodeBatchRequest, EncodeWordRequest
from api.steps.pedagogy import (
    build_decode_steps,
    build_encode_batch,
    build_encode_steps,
    map_decode_steps_from_entry,
    map_encode_steps_from_entry,
)
from api.steps.substance import build_compare_words_steps

router = APIRouter(prefix="/api/calc", tags=["calc"])


@router.post("/encode-word", response_model=WorkbenchResponse)
def encode_word(req: EncodeWordRequest) -> WorkbenchResponse:
    try:
        profile = AlphabetProfile(req.profile)
        entry = build_encode_steps(req.word, profile)
        if entry is None:
            raise ValueError(f"Keine gültige Substrat-Sequenz: {req.word!r}")
        steps = map_encode_steps_from_entry(entry) if req.include_steps else []
        result = {
            "word": entry["word"],
            "normalized": entry["normalized"],
            "substance": entry["substance"],
            "index": entry["index"],
            "content_hash": entry.get("content_hash", ""),
            "profile": profile.value,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return WorkbenchResponse(
        result=result,
        steps=steps,
        explain_links=["/erklaerungen/01-substanz-s", "/erklaerungen/02-index-i"],
    )


@router.post("/encode-batch", response_model=WorkbenchResponse)
def encode_batch(req: EncodeBatchRequest) -> WorkbenchResponse:
    try:
        profile = AlphabetProfile(req.profile)
        batch = build_encode_batch(req.text, profile)
        if req.include_steps:
            steps = []
            for word_entry in batch["words"]:
                steps.extend(map_encode_steps_from_entry(word_entry))
        else:
            steps = []
        result = {
            **batch,
            "words": [
                {
                    "word": w["word"],
                    "normalized": w["normalized"],
                    "substance": w["substance"],
                    "index": w["index"],
                    "content_hash": w.get("content_hash", ""),
                    "steps": map_encode_steps_from_entry(w) if req.include_steps else [],
                }
                for w in batch["words"]
            ],
            "profile": profile.value,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return WorkbenchResponse(
        result=result,
        steps=steps,
        explain_links=["/erklaerungen/01-substanz-s", "/erklaerungen/02-index-i"],
    )


@router.post("/decode-word", response_model=WorkbenchResponse)
def decode_word(req: DecodeWordRequest) -> WorkbenchResponse:
    try:
        profile = AlphabetProfile(req.profile)
        entry = build_decode_steps(req.substance, req.index, profile)
        if entry is None:
            raise ValueError("S und I passen nicht zu einer gültigen Wortsequenz.")
        steps = map_decode_steps_from_entry(entry) if req.include_steps else []
        result = {
            "substance": entry["substance"],
            "index": entry["index"],
            "word": entry["word"],
            "normalized": entry["normalized"],
            "ingredients": entry["ingredients"],
            "total_permutations": entry["total_permutations"],
            "content_hash": entry.get("content_hash", ""),
            "profile": profile.value,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return WorkbenchResponse(
        result=result,
        steps=steps,
        explain_links=["/erklaerungen/03-decode"],
    )


@router.post("/compare-words", response_model=WorkbenchResponse)
def compare_words(req: CompareWordsRequest) -> WorkbenchResponse:
    try:
        result, steps = build_compare_words_steps(req.a, req.b, req.profile)
        if not req.include_steps:
            steps = []
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return WorkbenchResponse(
        result=result,
        steps=steps,
        explain_links=["/erklaerungen/09-ggt-kgv", "/erklaerungen/10-wortpaar-diff"],
    )
