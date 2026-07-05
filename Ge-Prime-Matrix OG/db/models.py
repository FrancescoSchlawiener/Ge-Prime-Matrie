from dataclasses import dataclass

from ge_prime.decode import decode_word
from pipeline.normalize import denormalize_word


@dataclass
class StoredWord:
    id: int
    word_original: str
    word_normalized: str
    substance: int
    perm_index: int
    language: str | None
    source_id: int
    decoded: str
    display: str


def row_to_stored_word(row) -> StoredWord:
    """Build a StoredWord from a DB row with decoded and display forms."""
    normalized = row["word_normalized"]
    original = row["word_original"]
    substance = int(row["substance"])
    perm_index = row["perm_index"]
    decoded = decode_word(substance, perm_index)
    return StoredWord(
        id=row["id"],
        word_original=original,
        word_normalized=normalized,
        substance=substance,
        perm_index=perm_index,
        language=row["language"],
        source_id=row["source_id"],
        decoded=decoded,
        display=denormalize_word(normalized, original),
    )
