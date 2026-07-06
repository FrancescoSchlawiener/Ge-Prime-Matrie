"""Session store mit LRU und Dokument-Refs."""

from __future__ import annotations

import base64
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any

from alphabets import AlphabetProfile
from analysis.basis.index import BasisIndex
from analysis.document.model import GpmDocument


@dataclass
class StoredDocument:
    ref: str
    mode: str
    profile: AlphabetProfile
    document: GpmDocument | None = None
    hybrid: Any | None = None
    source_text: str = ""
    gpm_bytes: bytes | None = None
    language_id: str | None = None


@dataclass
class StoredIndex:
    index_id: str
    profile: AlphabetProfile
    partitions: dict[AlphabetProfile, BasisIndex]
    doc_refs: list[str] = field(default_factory=list)


class SessionStore:
    def __init__(self, max_refs: int = 500) -> None:
        self._documents: OrderedDict[str, StoredDocument] = OrderedDict()
        self._indexes: dict[str, StoredIndex] = {}
        self._max_refs = max_refs

    def put_document(
        self,
        *,
        mode: str,
        profile: AlphabetProfile,
        document: GpmDocument | None = None,
        hybrid: Any | None = None,
        source_text: str = "",
        gpm_bytes: bytes | None = None,
        language_id: str | None = None,
    ) -> str:
        import uuid

        ref = uuid.uuid4().hex
        while len(self._documents) >= self._max_refs:
            self._documents.popitem(last=False)
        self._documents[ref] = StoredDocument(
            ref=ref,
            mode=mode,
            profile=profile,
            document=document,
            hybrid=hybrid,
            source_text=source_text,
            gpm_bytes=gpm_bytes,
            language_id=language_id,
        )
        return ref

    def get_document(self, ref: str) -> StoredDocument:
        if ref not in self._documents:
            raise KeyError(f"Unbekannte document_ref: {ref!r}")
        self._documents.move_to_end(ref)
        return self._documents[ref]

    def put_index(
        self,
        partitions: dict[AlphabetProfile, BasisIndex],
        doc_refs: list[str],
        profile: AlphabetProfile,
    ) -> str:
        import uuid

        index_id = uuid.uuid4().hex
        self._indexes[index_id] = StoredIndex(
            index_id=index_id,
            profile=profile,
            partitions=partitions,
            doc_refs=list(doc_refs),
        )
        return index_id

    def get_index(self, index_id: str) -> StoredIndex:
        if index_id not in self._indexes:
            raise KeyError(f"Unbekannte index_id: {index_id!r}")
        return self._indexes[index_id]


store = SessionStore()


def document_to_dict(doc: GpmDocument) -> dict[str, Any]:
    return {
        "profile": doc.profile.value,
        "header": [
            {
                "word_id": e.word_id,
                "word_canonical": e.word_canonical,
                "word_normalized": e.word_normalized,
                "substance": e.substance,
                "perm_index": e.perm_index,
            }
            for e in doc.header
        ],
        "tokens": [
            {
                "word_id": t.word_id,
                "perm_index": t.perm_index,
                "case_code": t.case_code,
                "payload_kind": t.payload_kind.value if hasattr(t.payload_kind, "value") else str(t.payload_kind),
            }
            for t in doc.tokens
        ],
        "gaps": list(doc.gaps),
        "explicit": list(doc.explicit),
        "token_count": len(doc.tokens),
        "unique_words": len(doc.header),
    }


def gpm_bytes_to_b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")
