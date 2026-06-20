from dataclasses import dataclass
from typing import Iterable

from db.language import resolve_language
from ge_prime.encode import encode_word
from pipeline.normalize import normalize_word
from pipeline.sanitize import sanitize_line
from pipeline.tokenize import letters_only
from pipeline.validate import is_valid_normalized


@dataclass
class ProcessResult:
    word_original: str
    word_normalized: str
    substance: int
    perm_index: int
    language: str
    source: str


def process_token(
    token: str,
    *,
    language: str | None = None,
    source: str = "manual",
) -> ProcessResult | None:
    """Pipeline für extrahierte Tokens (Web: ignoriert Satzzeichen/Ziffern)."""
    cleaned = letters_only(token)
    if not cleaned:
        return None

    normalized = normalize_word(cleaned)
    if not is_valid_normalized(normalized):
        return None

    substance, perm_index = encode_word(normalized)
    return ProcessResult(
        word_original=cleaned,
        word_normalized=normalized,
        substance=substance,
        perm_index=perm_index,
        language=resolve_language(language),
        source=source,
    )


def process_word(
    raw: str,
    *,
    language: str | None = None,
    source: str = "manual",
) -> ProcessResult | None:
    """Pipeline für Scraper-Zeilen (strikt: Zeilen mit Ziffern/Satzzeichen verwerfen)."""
    cleaned = sanitize_line(raw)
    if cleaned is None:
        return None

    normalized = normalize_word(cleaned)
    if not is_valid_normalized(normalized):
        return None

    substance, perm_index = encode_word(normalized)
    return ProcessResult(
        word_original=cleaned,
        word_normalized=normalized,
        substance=substance,
        perm_index=perm_index,
        language=resolve_language(language),
        source=source,
    )


def process_lines(
    lines: Iterable[str],
    *,
    language: str | None = None,
    source: str = "unknown",
) -> tuple[list[ProcessResult], int]:
    accepted: list[ProcessResult] = []
    skipped = 0
    for line in lines:
        result = process_word(line, language=language, source=source)
        if result is None:
            skipped += 1
        else:
            accepted.append(result)
    return accepted, skipped
