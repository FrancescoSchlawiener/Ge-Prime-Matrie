"""Request-Modelle für Workbench-Endpoints."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import Base64Bytes, BaseModel, Field


class EncodeWordRequest(BaseModel):
    word: str = Field(max_length=100)
    profile: str = "og"
    include_steps: bool = True


class EncodeBatchRequest(BaseModel):
    text: str = ""
    profile: str = "og"
    include_steps: bool = True


class DecodeWordRequest(BaseModel):
    substance: int = Field(ge=1)
    index: int = Field(ge=0)
    profile: str = "og"
    include_steps: bool = True


class CompareWordsRequest(BaseModel):
    a: str = Field(max_length=100)
    b: str = Field(max_length=100)
    profile: str = "og"
    include_steps: bool = True


class CompileRequest(BaseModel):
    mode: Literal["nl", "code", "hybrid"]
    text: str = ""
    profile: str = "og"
    language_id: str | None = None
    content_key: str | None = Field(default=None, min_length=64, max_length=64)


class ReconstructRequest(BaseModel):
    mode: Literal["nl", "code", "hybrid"]
    document_ref: str


class GpmReadRequest(BaseModel):
    base64: Annotated[bytes, Base64Bytes] = Field(min_length=4)
    key: str | None = None


class GpmWriteRequest(BaseModel):
    document_ref: str
    profile: str = "og"
    encrypt: bool = False
    key: str | None = None


class SpectroscopeRequest(BaseModel):
    document_ref: str
    token_start: int = 0
    token_end: int = 0
    content_key: str | None = Field(default=None, min_length=64, max_length=64)


class GpmSearchRequest(BaseModel):
    document_ref: str
    query: str = ""
    mode: Literal["word", "gcd", "lcm"] = "word"
    queries: list[str] = Field(default_factory=list)


class WordPairRequest(BaseModel):
    a: str = Field(max_length=100)
    b: str = Field(max_length=100)
    profile: str = "og"
    mode: Literal["compare", "diff"] = "compare"


class AnagramSearchRequest(BaseModel):
    word: str = Field(max_length=100)
    profile: str = "og"
    limit: int = Field(default=100, ge=1, le=500)


class CompareDocumentsRequest(BaseModel):
    doc_a_ref: str
    doc_b_ref: str
    profile: str = "og"
    tier: int = Field(default=4, ge=0, le=4)


class ICurveRequest(BaseModel):
    doc_a_ref: str
    doc_b_ref: str
    profile: str = "og"


class CorpusIndexRequest(BaseModel):
    document_refs: list[str] = Field(max_length=500)
    profile: str = "og"
    extend_index_id: str | None = None


class CorpusQueryRequest(BaseModel):
    index_id: str
    query_ref: str
    top_k: int = Field(default=5, ge=1, le=50)
    tier: int = Field(default=1, ge=0, le=4)


class RedundancyScanRequest(BaseModel):
    document_ref: str
    canonical: bool = False
    window_mode: Literal["fixed", "adaptive"] = "fixed"
    window_min: int = 8
    window_max: int = 30
    window_size: int = 15
    structural_only: bool = False
    level: Literal["token", "block"] = "token"


class JobCompileRequest(BaseModel):
    mode: Literal["nl", "code", "hybrid"]
    text: str = ""
    profile: str = "og"
    language_id: str | None = None
    content_key: str | None = None


class JobRedundancyRequest(RedundancyScanRequest):
    pass


class JobCorpusIndexRequest(BaseModel):
    document_refs: list[str] = Field(max_length=500)
    profile: str = "og"
    extend_index_id: str | None = None


class CipherEncryptRequest(BaseModel):
    text: str
    key: str
    mode: str = "word"
    profile: str = "og"


class CipherRequest(BaseModel):
    base64_gpm: str
    key: str


class DocumentRefPayload(BaseModel):
    """Inline document for compare without prior compile session."""

    mode: Literal["nl", "code", "hybrid"] = "nl"
    text: str
    profile: str = "og"
    language_id: str | None = None


class CompareDocumentsInlineRequest(BaseModel):
    doc_a: DocumentRefPayload
    doc_b: DocumentRefPayload
    tier: int = Field(default=4, ge=0, le=4)


class SizeWordFallback(BaseModel):
    original: str = ""
    normalized: str = ""
    substance: int = Field(ge=1, default=1)
    perm_index: int = Field(ge=1, default=1)


class SizeEncodeWordRequest(BaseModel):
    content_hash: str = Field(min_length=64, max_length=64)
    profile: str = "og"
    fallback: SizeWordFallback | None = None


class SizeEncodeBatchRequest(BaseModel):
    word_hashes: list[str] = Field(min_length=1, max_length=50)
    profile: str = "og"


class SizeDecodeFallback(BaseModel):
    substance: int = Field(ge=1)
    perm_index: int = Field(ge=1)


class SizeDecodeRequest(BaseModel):
    content_hash: str = Field(min_length=64, max_length=64)
    profile: str = "og"
    fallback: SizeDecodeFallback | None = None
