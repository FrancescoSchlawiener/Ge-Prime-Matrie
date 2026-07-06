"""Cipher routes — encrypt / decrypt."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alphabets import AlphabetProfile
from analysis.security.cipher import decrypt_ciphertext, encrypt_text
from api.schemas.common import Step, WorkbenchResponse
from api.schemas.requests import CipherEncryptRequest, CipherRequest

router = APIRouter(prefix="/api/cipher", tags=["cipher"])


@router.post("/encrypt", response_model=WorkbenchResponse)
def cipher_encrypt(req: CipherEncryptRequest) -> WorkbenchResponse:
    try:
        result = encrypt_text(
            req.text,
            mode=req.mode,
            keys_raw=req.key,
            profile=AlphabetProfile(req.profile),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return WorkbenchResponse(
        result=result,
        steps=[Step(id="encrypt", title="Verschlüsselung", detail=f"Modus: {req.mode}", values={"tokens": result.get("token_count", 0)})],
        explain_links=["/erklaerungen/03-decode"],
    )


@router.post("/decrypt", response_model=WorkbenchResponse)
def cipher_decrypt(req: CipherRequest) -> WorkbenchResponse:
    try:
        result = decrypt_ciphertext(req.base64_gpm, keys_raw=req.key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return WorkbenchResponse(
        result=result,
        steps=[Step(id="decrypt", title="Entschlüsselung", detail="Chiffretext → Klartext.", values={"verified": result.get("verified", False)})],
    )
